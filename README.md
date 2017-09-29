# Flora
### Smart Contract Package Manager on IPFS


```
git clone https://github.com/Lamden/flora.git
python setup.py develop
flora --help
```

Flora is a simple package manager (for now) that allows users to register names, upload, and download packages in an encrypted manner. The current implementation uses SQL for demo purposes. This is not production ready.

```
flora install <username/package>
```

Users must register a name on Flora before uploading their packages with ```flora register <username>.``` Once a name is registered, the user is given an RSA key. The public key is stored on Flora to sign messages, and the private key is stored locally to decrypt them. Users can check if a name is available before registering with ```flora check <username>```.

After registering a username, packages can be uploaded. Instead of storing authentication credentials insecure plaintext methods seen in other package managers (like [PiPy](https://packaging.python.org/guides/migrating-to-pypi-org/#uploading])), Flora uses signed secrets to verify identity. When a user runs ```flora upload <username>/<package>```, given the package does not already exist, the server will generate a random secret and sign it with the stored public key for that user. That secret is sent back to the user as an authentication puzzle.

The server itself has an RSA key that it uses that is generated at runtime and never stored on hard disk. The server signs its own secret with that ephemeral key to prevent man-in-the-middle attacks (see [here](https://isis.poly.edu/~jcappos/papers/cappos_pmsec_tr08-02.pdf])).

The user decrypts the secret with its locally stored private key and then signs the package that it wants to upload with the newly solved secret. The secret now serves as a symmetrical key of proof. When the package is uploaded, it is encrypted. The server uses its private key to decode the secret that was stored on disk and then uses the solved secret to decrypt the payload that was sent by the user. If the payload is valid Solidity code and compiles without error, we can assume that the user's identity is true. This prevents certain attack vectors of other non-secure package managers.

For developers who just want to pull down code, using the command ```flora install <username>/<package>``` is sufficient. This will pull the package down and store it locally on their computer. Integration with Saffron to deploy these packages directly to chains is something to do.

Flora uses Templated Solidity which allows for metavariable assignment in the case that developers want to deploy multiple instances of a similar contract with only slight variable differences, or a user wants to provide a complex package and expose only certain variables for tuning so that installation of highly complex smart contracts is easy.

Templated Solidity looks like this:

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

And includes an example JSON payload to complete it that looks like this:

```
{
    'solidity_version':'0.4.15',
    'contract_name':'Testcoin',
    'symbol':'TST',
    'asset_name':'Testcoin',
    'total_supply':'1000000'
}
```

It's required to upload a Templated Solidity file with an example payload to Flora so that abstraction can occur later on. If there are no metavariables in a smart contract, the Templated Solidity can simply be vanilla Solidity with a blank example payload, as Templated Solidity is a superset of Solidity.

### TODO

Replace SQL driver with IPFS driver

Integrate with Saffron

Prepare a demo

Abstract classes and database structure to support potentially infinite smart contract languages

Solve DDOS and other public spamming attack vectors

Host a public instance

Other things that are on the backburner...