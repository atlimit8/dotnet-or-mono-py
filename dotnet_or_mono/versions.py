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
