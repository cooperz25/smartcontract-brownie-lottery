from brownie import accounts, network, config, Lottery, exceptions
from scripts import deploy, helper
from scripts.helper import DEV_NETWORK, getAccount
import pytest, time


def test_calculate():
    if network.show_active() in DEV_NETWORK:
        pytest.skip()
    lottery = deploy.deploy()

    acc = getAccount()

    # test start
    lottery.startLottery({"from": acc}).wait(1)
    assert lottery.state() == 0

    # test enter
    lottery.enterLottery({"from": acc, "value": lottery.getMinAmountUsdWei()}).wait(2)
    lottery.enterLottery({"from": acc, "value": lottery.getMinAmountUsdWei()}).wait(3)
    lottery.enterLottery({"from": acc, "value": lottery.getMinAmountUsdWei()}).wait(5)

    startBalance = acc.balance()
    lotteryBalance = lottery.balance()
    totalBalance = startBalance + lotteryBalance

    print(f"{startBalance} {lotteryBalance} {totalBalance}")

    # fund Link to contract
    helper.fundContract(lottery, 1 * 10 ** 17)

    # get random number
    tx = lottery.calculateLottery({"from": acc})
    assert lottery.state() == 2

    tx.wait(1)
    time.sleep(60)

    assert lottery.state() == 1
    assert lottery.recentWinner() == acc

    # test balance
    assert lottery.balance() == 0
