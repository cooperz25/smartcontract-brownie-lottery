// SPDX-License-Identifier: MIT

pragma solidity >=0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {
    uint256 MIN_USD = 50;
    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;

    enum State {
        STARTED,
        ENDED,
        CALCULATING_WINNER
    }
    State public state;
    address payable[] public players;
    address payable public recentWinner;
    AggregatorV3Interface internal ethUsdPriceFeed;
    event RandomNumberReq(bytes32 requestId);

    constructor(
        address _priceFeedContractAdd,
        address _vrf_cord_contract,
        address _link_token_contract,
        bytes32 _keyHash,
        uint256 _fee
    )
        VRFConsumerBase(
            _vrf_cord_contract, // VRF Coordinator
            _link_token_contract // LINK Token
        )
    {
        state = State.ENDED;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedContractAdd);

        keyHash = _keyHash;
        fee = _fee; // 0.1 LINK (Varies by network)
    }

    function startLottery() public onlyOwner {
        require(state == State.ENDED);
        state = State.STARTED;
    }

    function enterLottery() public payable {
        require(state == State.STARTED, "The lottery haven't started yet!");
        uint256 minAmountUsdWei = getMinAmountUsdWei();
        require(
            msg.value >= minAmountUsdWei,
            "The minimum ammount for lottery is 50USD"
        );
        players.push(payable(msg.sender));
    }

    function getMinAmountUsdWei() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        return (MIN_USD * 10**26) / uint256(price);
    }

    function calculateLottery() public onlyOwner {
        state = State.CALCULATING_WINNER;
        emit RandomNumberReq(getRandomNumber());
    }

    /**
     * Requests randomness
     */
    function getRandomNumber() public returns (bytes32 requestId) {
        require(
            LINK.balanceOf(address(this)) >= fee,
            "Not enough LINK - fill contract with faucet"
        );
        return requestRandomness(keyHash, fee);
    }

    /**
     * Callback function used by VRF Coordinator
     */
    function fulfillRandomness(bytes32 requestId, uint256 randomness)
        internal
        override
    {
        require(randomness > 0, "Fail random");
        randomResult = randomness;
        exportWinner(randomResult);
    }

    function exportWinner(uint256 _randomResult) public payable {
        recentWinner = players[_randomResult % players.length];
        recentWinner.transfer(address(this).balance);

        //reset
        players = new address payable[](0);
        state = State.ENDED;
    }
}
