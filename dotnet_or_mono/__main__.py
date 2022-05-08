#/bin/env python

"""
https://github.com/atlimit8/dotnet-or-mono-py

MIT License

Copyright (C) 2022  atlimit8 (Jason)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import subprocess
from assemblies import *
from versions import *

try:  # Forced testing
    from shutil import which
except ImportError:  # Forced testing
    try:
        from whichcraft import which
    except ImportError:  # Forced testing
        def which(path):
            path = subprocess.Popen(["which", path], shell=True, stdout=subprocess.PIPE).stdout.read().replace("\n", '').replace("\r", '')
            return path if path else None

def main(argv):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-mono", action="store_true",
        help="ignore Mono")
    parser.add_argument("--skip-dotnet", action="store_true",
        help="ignore Dotnet")
    subparsers = parser.add_subparsers(
        help='sub-command help')
    parser_run = subparsers.add_parser('run',
        help='run help')
    parser_run.set_defaults(command='run')
    parser_run.add_argument("run_assembly", type=ReadableAssembly, nargs=1,
        help="assembly to run")
    parser_run.add_argument("run_args", nargs="*",
        help="extra arguments passed to assembly",)
    parser_extract_assembly_framework = subparsers.add_parser('extract-assembly-framework', help='show help')
    parser_extract_assembly_framework.set_defaults(command='extract-assembly-framework')
    parser_extract_assembly_framework.add_argument("assemblies_to_analyze", type=ReadableAssembly, nargs='+', action="store",
        help="assemblies to analyze")
    parser_extract_assembly_framework.add_argument("--parts", nargs='+',
        choices=['internal', 'type', 'version', 'attributes', 'display', 'all'],
        default=['type', 'version', 'attributes', 'display'],
        help="parts of assembly's framework strings to show. internal - full internal string")
    #parser_show = subparsers.add_parser('show', help='show help')
    args = parser.parse_args()
    print(repr(args))
    if not args.skip_mono:
        mono_path = which('mono')
        if mono_path:
            print('mono: ' + mono_path)
        mono_version = get_mono_version()
        print('Mono Version: ' + ('.'.join(str(i) for i in mono_version) if mono_version else 'None'))
    if not args.skip_dotnet:
        dotnet_path = which('dotnet')
        if dotnet_path:
            print('dotnet: ' + dotnet_path)
        dotnet_version = get_dotnet_version()
        print('Dotnet Version: ' + ('.'.join(str(i) for i in dotnet_version) if dotnet_version else 'None'))
        available_dotnetcore_runtime_version = get_available_dotnetcore_runtime_versions()
        if available_dotnetcore_runtime_version:
            print('Dotnet Runtimes:')
            for runtime in available_dotnetcore_runtime_versions:
                print('    ' + runtime[0] + '\t' + '.'.join(runtime[1:]))
        available_dotnetcore_sdk_versions = get_available_dotnetcore_sdk_versions()
        if available_dotnetcore_sdk_versions:
            print('Dotnet SDKs:')
            for sdk in available_dotnetcore_sdk_versions():
                print('    ' + '.'.join(sdk))
    for assembly in args.assemblies_to_analyze:
        framework_type = AssemblyFrameworkType(assembly)
        if framework_type:
            print('Assembly: ' + assembly.name)
            if (('internal' in args.parts or 'all' in args.parts) and framework_type.internal_name is not None):
                print('Framework Internal: ' + framework_type.get_internal_string())
            if (('type' in args.parts or 'all' in args.parts) and framework_type.internal_name is not None):
                print('Framework Internal Type: ' + framework_type.internal_name)
            if (('version' in args.parts or 'all' in args.parts) and framework_type.version is not None):
                print('Framework Version: ' + '.'.join(framework_type.version))
            if (('attributes' in args.parts or 'all' in args.parts) and framework_type.attributes_string is not None):
                print('Framework Attributes: ' + framework_type.attributes_string)
            if ('display' in args.parts or 'all' in args.parts) and (framework_type.display_name is not None):
                print('Framework Display Name: ' + framework_type.display_name)

if __name__ == "__main__":
    import sys
    main(sys.argv)
