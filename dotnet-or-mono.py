#/bin/env python
import sys, shlex, subprocess, mmap, struct;

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

class ReadableAssembly:
    def __init__(self, filepath):
        name = None
        file = None
        def check_format():
            if file.read(2) != b'\x4D\x5A':
                return False
            return True
        for suffix in [ '', '.exe', '.dll' ]:
            try:
                name = filepath + suffix
                file = open(name, 'rb')
                if check_format():
                    break
            except:
                pass
            if file is not None:
                file.close()
                file = None
        if file is None:
            raise argparse.ArgumentTypeError(
                filepath + ', ' + filepath + '.exe, and ' + filepath + '.dll are not readable .NET assemblies.'
            )
        self.name = name
        self.file = file
    def fileno(self):
        if self.file:
            return self.file.fileno()
        raise IOError()
    def close(self):
        if self.file:
            self.file.close()



''' Generally extracts the framework type of an assembly by file path '''
class AssemblyFrameworkType:
    def __init__(self, file):
        mapped = None
        try:
            mapped = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
            self.internal_name = None
            self.version = None
            self.attributes_string = None
            self.display_name = None
            internal_end = mapped.rfind(b'\x01\x00T\x0e\x14FrameworkDisplayName')

            # 25 = len('\x01\x00T\x0e\x14FrameworkDisplayName')
            display_offset = internal_end + 25
            if internal_end == -1:
                internal_end = mapped.rfind(b'\x14FrameworkDisplayName')
                if end == -1:
                    return

                # 21 = len('\x14FrameworkDisplayName')
                display_offset = internal_end + 21

            display_length = struct.unpack('B', bytes(mapped[display_offset : display_offset + 1]))[0]
            self.display_name = mapped[display_offset + 1 : display_offset + 1 + display_length].decode("utf-8")

            # NOTE: will only work as long as Version is the first attribute
            type_end = mapped.rfind(b',Version=', internal_end - 200, internal_end)
            if type_end == -1:
                return (None, None, display_name)
            start = mapped.rfind(b'.NET', type_end - 64, type_end)
            self.internal_name = mapped[start : type_end].decode("utf-8")
            self.attributes_string = mapped[type_end + 1 : internal_end].decode("utf-8")
            version_end = self.attributes_string.find(',')
            version = (self.attributes_string[9:] if version_end == -1 else self.attributes_string[9:version_end]).split('.')
            if len(version):
                self.version = tuple(version)

        finally:
            if mapped is not None:
                mapped.close()
            if file is not None:
                file.close()

    '''Returns the version (tuple) for the minimum version of Mono that can host the assembly else None.'''
    def get_min_supported_mono_version(self):
        if (self.internal_name == '.NETStandard'):
            if (self.version is not None and len(self.version)):
                if (self.version[0] == 2):
                    if len(self.version) < 2 or self.version[1] == 0:
                        return (5, 4)
                    return (6, 4)
                if (self.version[0] == 1):
                    return (4, 6)
            return None
        if (self.internal_name == '.NETFramework'):
            if (self.version is not None and len(self.version)):
                if (self.version[0] == 4):
                    if len(self.version) < 2 or self.version[1] == 0:
                        return (2, 0)
                if (self.version[0] == 8):
                    return (6, 6)
                if (self.version[0] == 7):
                    if len(self.version) < 3 or self.version[2] == 0:
                        return (5, 10)
                    if self.version[2] == 1:
                        return (5, 10)
                    return (5, 18)
                if (self.version[0] == 6):
                    return (5, 18)
            if (self.version[0] == 5):
                    return (4, 4)
                # NOTE: Not supporting any version older
        return None

    '''Returns the version (tuple) for the minimum version of Mono that can host the assembly else None.'''
    def get_min_supported_core_runtime_version(self):
        if (self.internal_name == '.NETStandard'):
            if (self.version is not None and len(self.version)):
                if (self.version[0] == 2):
                    if len(self.version) < 2 or self.version[1] == 0:
                        return (2, 0)
                    return (3, 0)
                if (self.version[0] == 1):
                    return (1, 0)
            return None
        if (self.internal_name == '.NETCoreApp'):
            return version
        return None
    # TODO: ASP .NET Core

    def get_internal_string(self):
        return self.internal_name + ',' + self.attributes_string


try:  # Forced testing
    from shutil import which
except ImportError:  # Forced testing
    try:
        from whichcraft import which
    except ImportError:  # Forced testing
        def which(path):
            path = subprocess.Popen(["which", path], shell=True, stdout=subprocess.PIPE).stdout.read().replace("\n", '').replace("\r", '')
            return path if path else None


'''gets the Mono version as a tuple or None'''
def get_mono_version():
    try:
        first_line = subprocess.Popen(['mono', '--version'], stdout=subprocess.PIPE).stdout.readline().replace("\n", '').replace("\r", '')
        start = first_line.find('ersion ')
        if start == -1:
            return None
        start = start + 7
        end = first_line.find(' ', start)
        return tuple(int(i) for i in (first_line[start:len(first_line)] if end == -1 else first_line[start:end]).split('.'))
    except:
        return None

'''gets the Dotnet version as a tuple or None'''
def get_dotnet_version():
    try:
        line_pipe = subprocess.Popen(['dotnet', '--version'], stdout=subprocess.PIPE).stdout
        first_line = line_pipe.readline().replace('\n', '').replace('\r', '')
        return tuple(int(i) for i in first_line.split('.'))
    except:
        return None

'''gets the available .NET Core runtime versions as a list of tuples or None'''
def get_available_dotnetcore_runtime_versions():
    try:
        process = subprocess.Popen(['dotnet', '--list-runtimes'], stdout=subprocess.PIPE)
        line_pipe = process.stdout
        runtimes = []
        for line in line_pipe:
            parts = line.replace("\n", '').replace("\r", '').split(' ')
            runtimes.append(tuple([ parts[0] ] + parts[1].split('.')))
        return runtimes
    except:
        return None

'''gets the available .NET Core SDK versions as a list of tuples or None'''
def get_available_dotnetcore_sdk_versions():
    try:
        process = subprocess.Popen(['dotnet', '--list-sdks'], stdout=subprocess.PIPE)
        line_pipe = process.stdout
        runtimes = []
        for line in line_pipe:
            parts = line.replace("\n", '').replace("\r", '').split(' ')
            runtimes.append(tuple(parts[0].split('.')))
        return runtimes
    except:
        return None

if __name__ == "__main__":
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
        print('Dotnet Runtimes:')
        for runtime in get_available_dotnetcore_runtime_versions():
            print('    ' + runtime[0] + '\t' + '.'.join(runtime[1:]))
        print('Dotnet SDKs:')
        for sdk in get_available_dotnetcore_sdk_versions():
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
