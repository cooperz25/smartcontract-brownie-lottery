from brownie import accounts, network, config, Lottery, exceptions
from scripts import deploy, helper
from scripts.helper import DEV_NETWORK, getAccount
import pytest


def test_EntranceFee():
    lottery = deploy.deploy()
    entranceFee = lottery.getMinAmountUsdWei()
    assert entranceFee == 50 * 10 ** 18 / 3141


def test_Start():
    if network.show_active() not in DEV_NETWORK:
        pytest.skip()
    lottery = deploy.deploy()
    lottery.startLottery().wait(1)
    assert lottery.state() == 0


def test_enter():
    if network.show_active() not in DEV_NETWORK:
        pytest.skip()
    lottery = deploy.deploy()

    # test start
    lottery.startLottery().wait(1)
    assert lottery.state() == 0

    # test enter
    acc = getAccount()
    lottery.enterLottery({"value": lottery.getMinAmountUsdWei()}).wait(1)
    assert lottery.players(0) == acc


def test_enter_unless_started():
    if network.show_active() not in DEV_NETWORK:
        pytest.skip()
    lottery = deploy.deploy()

    acc = getAccount()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enterLottery({"value": lottery.getMinAmountUsdWei()}).wait(1)


def test_calculate():
    if network.show_active() not in DEV_NETWORK:
        pytest.skip()
    lottery = deploy.deploy()

    # test start
    lottery.startLottery().wait(1)
    assert lottery.state() == 0

    # test enter
    acc = getAccount()
    acc1 = getAccount(1)
    acc2 = getAccount(2)

    lottery.enterLottery({"from": acc, "value": lottery.getMinAmountUsdWei()}).wait(1)
    lottery.enterLottery({"from": acc1, "value": lottery.getMinAmountUsdWei()}).wait(1)
    lottery.enterLottery({"from": acc2, "value": lottery.getMinAmountUsdWei()}).wait(1)

    startBalance = acc2.balance()
    lotteryBalance = lottery.balance()
    totalBalance = startBalance + lotteryBalance

    # fund Link to contract
    helper.fundContract(lottery, 1 * 10 ** 17)

    # get random number
    tx = lottery.calculateLottery()
    tx.wait(1)
    assert lottery.state() == 2
    reqId = tx.events["RandomNumberReq"]["requestId"]

    vrfContractMock = helper.getContract("vrf_cord_contract")
    vrfContractMock.callBackWithRandomness(reqId, 2525, lottery)

    assert lottery.state() == 1
    assert lottery.randomResult() == 2525
    assert lottery.recentWinner() == acc2

    # test balance
    assert acc2.balance() == totalBalance
