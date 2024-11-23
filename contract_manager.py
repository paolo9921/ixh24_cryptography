from web3 import Web3
from solcx import compile_source
from solcx import install_solc, set_solc_version

class ContractManager:
    def __init__(self):

        install_solc('0.8.0')
        set_solc_version('0.8.0')
        # Connect to a local Ethereum node (e.g., Ganache)
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to the Ethereum node.")

        # Set default account (use the first account from Ganache)
        self.w3.eth.default_account = self.w3.eth.accounts[0]

        # Compile the smart contract
        compiled_sol = compile_source('''
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
        ''')

        contract_id, contract_interface = compiled_sol.popitem()

        # Get ABI and bytecode
        self.abi = contract_interface['abi']
        self.bytecode = contract_interface['bin']

        self.contract = None
        self.contract_address = None

    def deploy_contract(self):
        # Deploy the contract
        UniversityVotes = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = UniversityVotes.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.contract_address = tx_receipt.contractAddress
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)
        return self.contract_address

    def submit_votes(self, university_id, votes):
        # Submit votes to the contract
        tx_hash = self.contract.functions.submitVotes(university_id, votes).transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    def get_votes(self, university_id):
        # Get votes from the contract
        votes = self.contract.functions.getUniversityVotes(university_id).call()
        return votes
