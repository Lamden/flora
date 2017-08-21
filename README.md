# Flora
### Smart Contract Package Mangager on IPFS

Flora is how you install smart contracts on your Hadron chain instances. It's as simple as running `flora install erc20` inside of your project directory. Smart contracts are stored on IPFS, so they are distributed around the world. Uploading your own is super easy as well. Just run ```flora upload my-package.tsol --name awesome-package --example example-payload.json```.

Smart contracts are stored in .tsol files instead of .sol files. This is because smart contract packages are made to be customizable. A .tsol file uses {{handlebars}} to denote variables that can be adjusted. Here's an example:

```
pragma solidity ^{{solidity_version}};

contract {{contract_name}} {
    string public constant symbol = "{{symbol}}";
    string public constant name = "{{asset_name}}";
    uint8 public constant decimals = 18;
    uint256 _totalSupply = {{total_supply}};

    address public owner;
    mapping(address => uint256) balances;
    mapping(address => mapping (address => uint256)) allowed;
    
```

This is an ERC20 token contract that can be modified on the fly and reused as an asset factory. When uploading to Flora, you have to provide a payload that compiles successfully. An example of this looks like:

```
{
    'solidity_version':'0.4.15',
    'contract_name':'Testcoin',
    'symbol':'TST',
    'asset_name':'Testcoin',
    'total_supply':'1000000'
}
```

You save the .tsol and example payload seperately, and then upload them together. If they compile successfully, and the name you choose is globally unique, it will be on IPFS for others to download across the world.

You can deploy .tsol files with the Hadron Wrapper CLI tool.

For now, Flora is simply a document store. In the future, it will support multiple smart contract languages for different blockchain technologies, usernames, dependencies, and more.