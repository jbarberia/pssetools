#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config Generator: Create multiple simulation configs from a template
Useful for batch processing: 10+ similar cases with different parameters
"""

import os
import json
import sys
import argparse


def load_template(template_path):
    """Load template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_variables(variables_path):
    """Load variables from JSON file"""
    with open(variables_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def substitute(content, variables_dict):
    """Replace {{KEY}} with values from variables_dict"""
    result = content
    for key, value in variables_dict.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))
    return result


def generate_configs(template_path, variables_path, output_dir, output_format="separate"):
    """
    Generate config files from template and variables
    
    Args:
        template_path: Path to template file with {{VAR}} placeholders
        variables_path: Path to JSON file with variables
        output_dir: Directory to save generated configs
        output_format: "separate" (one file per case) or "combined" (one file with all)
    
    Returns:
        List of generated file paths
    """
    template_content = load_template(template_path)
    variables_data = load_variables(variables_path)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    generated_files = []
    
    # Determine if variables has a list of case definitions
    if isinstance(variables_data, dict):
        if 'cases' in variables_data and isinstance(variables_data['cases'], list):
            cases = variables_data['cases']
        else:
            cases = [variables_data]
    else:
        cases = variables_data if isinstance(variables_data, list) else [variables_data]
    
    if output_format == "combined":
        # All cases in one file
        combined_content = "# Combined simulation config\n"
        combined_content += "# Generated from template: {}\n".format(
            os.path.basename(template_path))
        combined_content += "# Generated with {} cases\n\n".format(len(cases))
        combined_content += "simulations:\n"
        
        for i, case_vars in enumerate(cases):
            case_content = substitute(template_content, case_vars)
            combined_content += case_content
            if i < len(cases) - 1:
                combined_content += "\n"
        
        output_file = os.path.join(output_dir, "config_combined.yml")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_content)
        generated_files.append(output_file)
        print("[OK] Generated combined config: {}".format(output_file))
    
    else:
        # One file per case
        for case_vars in cases:
            case_content = substitute(template_content, case_vars)
            
            # Generate output filename
            if 'CASE_NAME' in case_vars:
                case_name = case_vars['CASE_NAME']
                filename = "config_{}.yml".format(case_name)
            else:
                filename = "config_case_{}.yml".format(len(generated_files) + 1)
            
            output_file = os.path.join(output_dir, filename)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(case_content)
            generated_files.append(output_file)
            print("[OK] Generated: {}".format(filename))
    
    return generated_files


def _execute(template, variables, output, combined=False):
    """Internal execution function"""
    output_format = "combined" if combined else "separate"
    
    print("[*] Generating configs from template: {}".format(template))
    print("[*] Using variables: {}".format(variables))
    print("[*] Output format: {}".format(output_format))
    
    try:
        generated_files = generate_configs(
            template,
            variables,
            output,
            output_format=output_format
        )
        
        print("\n[OK] Generated {} config file(s)".format(len(generated_files)))
        print("[*] Output directory: {}".format(os.path.abspath(output)))
        
        return 0
    
    except Exception as e:
        print("[ERROR] {}".format(str(e)))
        return 1


def run(**kwargs):
    """Entry point for CLI integration"""
    template = kwargs.get('template')
    variables = kwargs.get('variables')
    output = kwargs.get('output', '.')
    combined = kwargs.get('combined', False)
    
    if template and variables:
        return _execute(template, variables, output, combined)
    else:
        main()


def main():
    parser = argparse.ArgumentParser(
        description='Generate simulation configs from template and variables',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pssetools gen-config -t template.yml -v vars.json -o ./configs
  pssetools gen-config -t template.yml -v vars.json -o . --combined
        """)
    
    parser.add_argument('-t', '--template', required=True,
                        help='Template file with {{VARIABLE}} placeholders')
    parser.add_argument('-v', '--variables', required=True,
                        help='JSON file with variable values')
    parser.add_argument('-o', '--output', default='.',
                        help='Output directory for generated configs')
    parser.add_argument('--combined', action='store_true',
                        help='Generate single combined config instead of separate files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.template):
        print("[ERROR] Template file not found: {}".format(args.template))
        sys.exit(1)
    
    if not os.path.exists(args.variables):
        print("[ERROR] Variables file not found: {}".format(args.variables))
        sys.exit(1)
    
    sys.exit(_execute(args.template, args.variables, args.output, args.combined))


if __name__ == '__main__':
    main()
