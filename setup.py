#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools


def readme():
  return '`pstar` documentation and source code can be found at https://github.com/iansf/pstar.'


def version():
  return '0.1.9'


setuptools.setup(
    name='pstar',
    description='pstar: numpy for arbitrary data',
    long_description=readme(),
    long_description_content_type='text/markdown',
    version=version(),
    url='https://github.com/iansf/pstar',
    download_url='https://github.com/iansf/pstar/archive/%s.tar.gz' % version(),
    author='Ian Fischer, Google',
    author_email='iansf@google.com',
    packages=['pstar'],
    license='Apache 2.0',
    install_requires=['qj'],
    test_suite='nose.collector',
    tests_require=['matplotlib', 'mock', 'nose'],
)
