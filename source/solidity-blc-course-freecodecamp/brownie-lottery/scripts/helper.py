from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    LinkToken,
    VRFCoordinatorMock,
    Contract,
)


DEV_NETWORK = ["development", "gananche-local"]
MAINNET_FORK = ["mainnet-fork-dev", "mainnet-fork-dev2"]

name_to_mock = {
    "eth_usd_price_feed_contract": MockV3Aggregator,
    "vrf_cord_contract": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def getAccount(index=None, networkId=None):
    if network.show_active() in DEV_NETWORK or network.show_active() in MAINNET_FORK:
        if index:
            return accounts[index]
        if networkId:
            return accounts.load(networkId)
        return accounts[0]

    # default
    return accounts.add(config["wallets"]["key"])


def getContract(contractName):
    contractType = name_to_mock[contractName]
    if network.show_active() in DEV_NETWORK:
        if len(contractType) <= 0:
            return deployMockContract(contractName)
        return contractType[-1]
    else:
        contract_address = config["networks"][network.show_active()][contractName]
        contract = Contract.from_abi(
            contractType._name, contract_address, contractType.abi
        )
        return contract


def deployMockContract(contractName):
    if contractName == "eth_usd_price_feed_contract":
        return MockV3Aggregator.deploy(8, 314100000000, {"from": getAccount()})
    if contractName == "vrf_cord_contract":
        return VRFCoordinatorMock.deploy(
            getContract("link_token"), {"from": getAccount()}
        )
    if contractName == "link_token":
        return LinkToken.deploy({"from": getAccount()})


def getKeyHash():
    return config["networks"][network.show_active()]["key_hash"]


def getFee():
    return config["networks"][network.show_active()]["fee"]


def fundContract(targetContract, value):
    linkContract = getContract("link_token")
    linkContract.transfer(targetContract, value, {"from": getAccount()}).wait(1)


def getIsPublish(_networkName):
    if (
        _networkName in DEV_NETWORK
        or _networkName in MAINNET_FORK
        or _networkName == "kovan"
    ):
        return False
    else:
        return True
