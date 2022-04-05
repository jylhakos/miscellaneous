# Blockchain and Supply Chain

The document contains information to implement supply chain application using open source blockchain libraries.

The stakeholders use blockchain to track and record products in a supply 
chain network.

The application defines the customized transaction processor from blockchain for its supply chain requirements.

A transaction is an event that changes the state of the blockchain.

A batch is the state change in the blockchain which contains transactions.

The application submits new transactions to the validator network and fetch the resulting state and block data from the blockchain provided by Hyperledger Sawtooth.

The applications are supply chain clients that connect to validator and query the state of the blockchain and submit batches.

The first node in blockchain creates the genesis block, which specifies the initial settings for the peer-to-peer network.

Each block on the blockchain is linked by a cryptographic hash to the previous block.

The application interacts with the blockchain network by sending a transaction while transaction processor validates the transaction and applies the changes to the state, and adds the transaction into the next block.

The blockchain validation process checks for transaction permissions to verify the entity who is allowed to issue blocks and batches.

The node uses consensus algorithm in processing blockchain to reach agreement among a group of participants nodes on peer-to-peer network.

A database stores a local record of transactions for the
blockchain.

The deployment utilizes Docker for blockchain on peer-to-peer network.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/SupplyChain/1.png?raw=true)

Figure: A node consists of REST API, Validator and Transaction Processor in peer-to-peer network for Supply Chain

### References

https://sawtooth.hyperledger.org/

https://github.com/hyperledger/sawtooth-core

