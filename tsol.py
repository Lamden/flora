# tsol libs
from solc import compile_source, compile_standard
from jinja2 import Environment, Template
from jinja2.nodes import Name
from io import BytesIO
import json

BASE_JSON_PAYLOAD = '''{"language": "Solidity", "sources": {
				"{{name}}": {
					"content": {{sol}}
				}
			},
			"settings": {
				"outputSelection": {
					"*": {
						"*": [ "metadata", "evm.bytecode", "abi", "evm.bytecode.opcodes", "evm.gasEstimates", "evm.methodIdentifiers" ]
					}
				}
			}
		}'''

def does_compile(template, example):
	try:
		compile(template, example)
	except:
		return False
	return True

def compilation_payload_from_paths(template, example):
	code = open(template)

	# turn the example into a dict
	payload = None
	with open(example) as e:    
		payload = json.load(e)
	solidity = load_tsol_file(code, payload)
	return Environment().from_string(BASE_JSON_PAYLOAD).render(name=solidity[0], sol=json.dumps(solidity[1]))

def generate_code(template, example):
	return(Template(template).render(example))

def generate_compilation_payload(template, example):
	sol = json.dumps('{}'.format(template.read()))
	name = example['contract_name']
	base = Template(BASE_JSON_PAYLOAD).render(sol=sol, name=name)
	code = Template(base).render(example)
	return code

def compile(template, example):
	g = generate_compilation_payload(template, example)
	j = json.loads(g)
	return compile_standard(j)
