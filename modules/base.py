import asyncio
import random
import time

import aiohttp
from eth_account.messages import encode_defunct, encode_typed_data, _hash_eip191_message
from hexbytes import HexBytes
from loguru import logger
from web3.types import TxParams

from libs.eth_async.client import Client
from libs.eth_async.data.models import TokenAmount, TxArgs, Networks
from libs.eth_async.utils.utils import randfloat

from data.models import Settings, Contracts
from utils.db_api.models import Wallet
from utils.logs_decorator import controller_log


class Base:
    __module__ = 'Web3 Base'
    def __init__(self, client: Client):
        self.client = client
        self.settings = Settings()

    @controller_log("Wrap Controller")
    async def wrap_controller(self):
        wraps = random.randint(1, 4)
        results = []
        text = f'{wraps} Wraps:'
        results.append(text)

        for wrap in range(wraps):
            try:
                balance = await self.client.wallet.balance()

                amount = TokenAmount(amount=float(balance.Ether) * self.percent)
                wrp = await self.wrap_eth(amount=amount)
                result = f"{amount}"
                results.append(result)

            except Exception as e:
                result = f"Wrap Failed | {e}"
                results.append(result)
                pass

        await asyncio.sleep(random.randint(2, 6))
        try:
            balance = await self.client.wallet.balance(token=Contracts.WETH)
            unwrap = await self.unwrap_eth(amount=balance)

            result = f"Unwapped: {balance}"
            results.append(result)

        except Exception as e:
            result = f"Unwrap Failed | {e}"
            results.append(result)
            pass

        return results
    @staticmethod
    async def get_token_price(token_symbol='ETH', second_token: str = 'USDT') -> float | None:
        token_symbol, second_token = token_symbol.upper(), second_token.upper()

        if token_symbol.upper() in ('USDC', 'USDC.E', 'USDT', 'DAI', 'CEBUSD', 'BUSD'):
            return 1
        if token_symbol == 'WETH':
            token_symbol = 'ETH'
        if token_symbol == 'USDC.E':
            token_symbol = 'USDC'

        if token_symbol == 'KLAY':
            token_symbol = 'KAIA'
            # for _ in range(5):
            #     try:
            #         async with aiohttp.ClientSession() as session:
            #             async with session.get(f'https://api.allbit.com/token/v1/klaytn/scope/token/0x0000000000000000000000000000000000000000') as r:
            #                 if r.status != 200:
            #                     return None
            #                 result_dict = await r.json()
            #                 if 'data' not in result_dict:
            #                     return None
            #                 return float(result_dict['data']['currentPrice'])
            #     except Exception as e:
            #         await asyncio.sleep(5)

        for _ in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f'https://api.binance.com/api/v3/depth?limit=1&symbol={token_symbol}{second_token}') as r:
                        if r.status != 200:
                            return None
                        result_dict = await r.json()
                        if 'asks' not in result_dict:
                            return None
                        return float(result_dict['asks'][0][0])
            except Exception as e:
                await asyncio.sleep(5)
        raise ValueError(f'Can not get {token_symbol + second_token} price from Binance')

    async def approve_interface(self, token_address, spender, amount: TokenAmount | None = None) -> bool:
        balance = await self.client.wallet.balance(token=token_address)
        if balance.Wei <= 0:
            return False

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = await self.client.transactions.approved_amount(
            token=token_address,
            spender=spender,
            owner=self.client.account.address
        )

        if amount.Wei <= approved.Wei:
            return True

        #print(f'Trying to approve: {token_address} {amount.Ether} - {amount.Wei}')

        tx = await self.client.transactions.approve(
            token=token_address,
            spender=spender,
            amount=amount
        )
        # push = await self.push_tx(
        #     tx_params=tx
        # )
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        if receipt:
            return True

        return False

    async def get_token_info(self, contract_address):
        contract = await self.client.contracts.default_token(contract_address=contract_address)
        print('name:', await contract.functions.name().call())
        print('symbol:', await contract.functions.symbol().call())
        print('decimals:', await contract.functions.decimals().call())

    @staticmethod
    def parse_params(params: str, has_function: bool = True):
        if has_function:
            function_signature = params[:10]
            print('function_signature', function_signature)
            params = params[10:]
        while params:
            print(params[:64])
            params = params[64:]

    @staticmethod
    def get_eth_amount_for_swap():
        settings = Settings()
        return TokenAmount(
            amount=randfloat(
                from_=settings.eth_amount_for_swap.from_,
                to_=settings.eth_amount_for_swap.to_,
                step=0.0000001
            )
        )

    @staticmethod
    def get_eth_amount_for_bridge():
        settings = Settings()
        return TokenAmount(
            amount=randfloat(
                from_=settings.eth_amount_for_bridge.from_,
                to_=settings.eth_amount_for_bridge.to_,
                step=0.0000001)
        )

    def get_session(self):
        #if self.client.proxy:
        #    return ProxyConnector.from_url(self.client.proxy)
        return None

    async def sign_message(
            self,
            text: str = None,
            typed_data: dict = None,
            hash: bool = False
    ):
        if text:
            message = encode_defunct(text=text)
        elif typed_data:
            message = encode_typed_data(full_message=typed_data)
            if hash:
                message = encode_defunct(hexstr=_hash_eip191_message(message).hex())

        signed_message = self.client.account.sign_message(message)

        signature = signed_message.signature.hex()

        if not signature.startswith('0x'): signature = '0x' + signature
        return signature


    async def send_eth(self, to_address, amount: TokenAmount):

        tx_params = TxParams(
            to=to_address,
            data='0x',
            value=amount.Wei
        )

        tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
        await asyncio.sleep(random.randint(2, 4))
        receipt = await tx.wait_for_receipt(client=self.client, timeout=300)
        if receipt:
            return (f'Balance Sender | Success send {amount.Ether:.5f} ETH to {to_address}')

        else:
            return f'Balance Sender | Failed'

    async def wait_tx_status(self, tx_hash: HexBytes, max_wait_time=100) -> bool:
        start_time = time.time()
        while True:
            try:
                receipts = await self.client.w3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    return True
                elif status is None:
                    await asyncio.sleep(0.3)
                else:
                    return False
            except BaseException:
                if time.time() - start_time > max_wait_time:
                    logger.exception(f'{self.client.account.address} получил неудачную транзакцию')
                    return False
                await asyncio.sleep(3)

    async def get_usd_gas(self, data, tx):
        eth_price = await self.get_token_price('ETH')

        contract = await self.client.contracts.get(contract_address=Contracts.OracleL1)

        l1_fee = TokenAmount(
            amount= await contract.functions.getL1Fee(data).call(),
            wei=True
            )

        gas_eth = TokenAmount(
            amount= int(tx['gas']) * (int(tx['maxFeePerGas'])),
                                      #+ int(tx['maxPriorityFeePerGas'])),
            wei=True
        )

        usd_gas_price = float((l1_fee.Ether + gas_eth.Ether)) * eth_price

        return usd_gas_price

    async def wrap_eth(self, amount: TokenAmount = None):
            success_text = f'BASE | Wrap ETH | Success | {amount.Ether:.5f} ETH'
            failed_text = f'BASE | Wrap ETH | Failed | {amount.Ether:.5f} ETH'

            if self.client.network == Networks.Ethereum:
                weth =Contracts.WETH_ETHEREUM
            else:
                weth = Contracts.WETH

            contract = await self.client.contracts.get(contract_address=weth)

            encode = contract.encode_abi("deposit", args=[])
            #print(encode)
            tx_params = TxParams(
                to=contract.address,
                data=encode,
                value=amount.Wei
            )

            tx_label = f"Wrapped {amount.Ether:.5f}"

            tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
            await asyncio.sleep(random.randint(2, 4))
            receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

            if receipt:

                return tx_label


    async def unwrap_eth(self, amount: TokenAmount = None):


            if self.client.network == Networks.Ethereum:
                weth =Contracts.WETH_ETHEREUM
            else:
                weth = Contracts.WETH

            if not amount:
                amount = await self.client.wallet.balance(token=weth)

            contract = await self.client.contracts.get(contract_address=weth)

            data = TxArgs(
                wad = amount.Wei
            ).tuple()

            encode = contract.encode_abi("withdraw", args=data)
            #print(encode)
            tx_params = TxParams(
                to=contract.address,
                data=encode,
                value=0
            )

            tx_label = f"Unwrapper {amount.Ether:.5f}"

            tx = await self.client.transactions.sign_and_send(tx_params=tx_params)
            await asyncio.sleep(random.randint(2, 4))
            receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

            if receipt:

                return tx_label


    async def push_tx(self,
                      tx_params,
                      success_text: str = None,
                      failed_text: str = None
                      ):
        try:
            tx = await self.client.transactions.auto_add_params(tx_params=tx_params)

            gas_usd = await self.get_usd_gas(data=tx['data'], tx=tx)

            if gas_usd < self.settings.max_gas_price:

                tx = await self.client.transactions.sign_and_send(tx_params=tx)
                await asyncio.sleep(random.randint(2, 4))
                receipt = await tx.wait_for_receipt(client=self.client, timeout=300)

                if receipt:
                    return f'{success_text} | GAS {gas_usd:.3f} USD'

            else:
                logger.warning(f'{failed_text} | GAS {gas_usd:.3f} | More than min_gas: '
                               f'{self.settings.max_gas_price:.3f} USD')

                return f'{failed_text}'

        except Exception as e:

            return f'{failed_text} | Error: {e}'
