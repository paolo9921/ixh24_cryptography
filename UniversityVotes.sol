pragma solidity ^0.8.0;

contract UniversityVotes {
    struct UniversityResult {
        uint[] votes;
        bool submitted;
    }
    
    mapping(uint => UniversityResult) public universityResults;
    address public owner;
    bool public votingEnded;
    
    event ResultSubmitted(uint universityId, uint[] votes);
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    function submitVotes(uint universityId, uint[] memory votes) public {
        require(!universityResults[universityId].submitted, "Results already submitted for this university");
        
        universityResults[universityId] = UniversityResult({
            votes: votes,
            submitted: true
        });
        
        emit ResultSubmitted(universityId, votes);
    }
    
    function getUniversityVotes(uint universityId) public view returns (uint[] memory) {
        require(universityResults[universityId].submitted, "No results for this university");
        return universityResults[universityId].votes;
    }
    
    function endVoting() public onlyOwner {
        votingEnded = true;
    }
}