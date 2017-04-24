import os, json
from jsonschema import RefResolver, Draft4Validator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

schema_path = os.path.join(os.path.dirname(__file__), "./json-schemas")
instance_path = os.path.join(os.path.dirname(__file__), "./json-instances")

def validate(instance_filename, schema_filename, software_type, print_errors):
    try:
        schema_filepath = os.path.join(schema_path, schema_filename)
        definitions_filepath = os.path.join(schema_path, "definitions.json")

        schema_file = open(schema_filepath)
        definitions_file = open(definitions_filepath)

        schema = json.load(schema_file)
        definitions = json.load(definitions_file)

        resolver = RefResolver('file://' + definitions_filepath, definitions)
        validator = Draft4Validator(schema, resolver=resolver)

        print("Validating %s in %s against %s" % (software_type.lower(), instance_filename, schema_filename))

        try:
            instance_file = open(os.path.join(instance_path, instance_filename))
            instance = json.load(instance_file)

            has_errors = False
            for key in instance:
                if key != "settings" and instance[key]["directory"] == software_type:
                    errors = sorted(validator.iter_errors(instance[key]), key=lambda e: e.path)

                    if not print_errors:
                        for error in errors:
                            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                                print(list(suberror.schema_path), suberror.message, sep=", ")
                    elif print_errors:
                        for error in errors:
                            print("\tError:", key, "-", error.message)

            return has_errors

        finally:
            instance_file.close()

    finally:
        schema_file.close()
        definitions_file.close()

'''def validate_instances(schema_filename, print_errors):
    result = True
    instance_files = [f for f in os.listdir(instance_path) if os.path.isfile(os.path.join(instance_path, f))]
    for instance_file in instance_files:
        result = result and validate_instance(instance_file, schema_filename, print_errors)
    return result
'''

def validate_schema(filename):
    try:
        schema_file = open(os.path.join(schema_path, filename))
        schema = json.load(schema_file)

        try:
            Draft4Validator.check_schema(schema)
            return True
        except:
            logger.error(e)
            return False
    finally:
        schema_file.close()

def validate_schemas():
    result = True
    schema_files = [f for f in os.listdir(schema_path) if os.path.isfile(os.path.join(schema_path, f))]
    for schema_file in schema_files:
        print("Validating %s" % schema_file)

        is_valid = validate_schema(schema_file)
        if not is_valid:
            print("\tInvalid schema")

        result = result and is_valid

    return result

def main():
    print("VALIDATING SCHEMAS\n------------------")
    result = validate_schemas()
    if result:
        print("All schemas are valid")
    else:
        print("Schemas invalid")

    print("\nVALIDATING DISEASE TRANSMISSION MODELS\n--------------------------------------")
    result = validate("software.json", "disease_transmission_models_schema.json", "Disease transmission models", True)

if __name__ == "__main__":
    main()