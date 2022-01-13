from brownie import accounts, config, network, Lottery
from scripts import helper
import time


def deploy():
    acc = helper.getAccount()

    # deploy contract
    lotteryContract = Lottery.deploy(
        helper.getContract("eth_usd_price_feed_contract").address,
        helper.getContract("vrf_cord_contract").address,
        helper.getContract("link_token").address,
        helper.getKeyHash(),
        helper.getFee(),
        {"from": acc},
        publish_source=helper.getIsPublish(network.show_active()),
    )
    print("price: ", lotteryContract.getMinAmountUsdWei())
    return lotteryContract


def startLottery():
    # start the game
    print("Start Lottery: ")
    Lottery[-1].startLottery().wait(1)


def enterLottery():
    print("Enter Lottery: ")
    Lottery[-1].enterLottery({"from": helper.getAccount(), "value": 2 * 10 ** 16}).wait(
        2
    )


def calculate():
    lotteryContract = Lottery[-1]
    helper.fundContract(lotteryContract, 1 * 10 ** 17)
    lotteryContract.calculateLottery({"from": helper.getAccount()}).wait(1)


def showRandom():
    lotteryContract = Lottery[-1]
    print(lotteryContract.randomResult())
    print(lotteryContract.recentWinner())


def main():
    deploy()
    startLottery()

    enterLottery()
    enterLottery()

    calculate()
    time.sleep(120)
    showRandom()
