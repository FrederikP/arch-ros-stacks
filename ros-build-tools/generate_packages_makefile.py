#!/usr/bin/env python

import os.path
import subprocess
import sys


MAKEFILE_TARGET = """%(package)s/.built: %(dependency_string)s
\tcd %(package)s; makepkg -i -f
\ttouch %(package)s/.built

"""


class InvalidPackage(Exception):
  def __init__(self, package):
    self.package = package

  def __str__(self):
    return repr(self.package)


class RosDependencyCache(object):

  def __init__(self):
    self._dependencies = {}

  def add_package_directory(self, name):
    pkgbuild_file = os.path.realpath(name + '/PKGBUILD')
    if not os.path.exists(pkgbuild_file):
      raise InvalidPackage(name)
    aur_package_name = get_package_name(pkgbuild_file)
    if len(aur_package_name) == 0:
      raise InvalidPackage(name)
    ros_dependencies = get_ros_dependencies(pkgbuild_file)
    self._dependencies[aur_package_name] = ros_dependencies

  def get_packages(self):
    return list(self._dependencies.keys())

  def get_dependencies(self, package_name, remove_unknown=True):
    package_dependencies = self._dependencies.get(package_name)
    if package_dependencies is None:
      raise InvalidPackage(package_name)
    if not remove_unknown:
      return package_dependencies
    return [dependency for dependency in package_dependencies
            if self._dependencies.get(dependency)]


def get_pkgbuild_variable(pkgbuild, variable, is_array=False):
  if is_array:
    array_string = '[@]'
  else:
    array_string = ''
  with subprocess.Popen(
      'source %s && echo ${%s%s}' % (pkgbuild, variable, array_string),
      shell=True, stdout=subprocess.PIPE) as shell_process:
    if is_array:
      return shell_process.stdout.readline().decode().split()
    else:
      return shell_process.stdout.readline().decode().strip()


def get_ros_dependencies(pkgbuild):
  return get_pkgbuild_variable(pkgbuild, 'ros_depends', is_array=True)


def get_package_name(pkgbuild):
  return get_pkgbuild_variable(pkgbuild, 'pkgname')


def generate_makefile(cache):
  makefile = ''
  for package in cache.get_packages():
    dependency_string = ''
    for dependency in cache.get_dependencies(package):
      dependency_string += dependency + '/.built '
    makefile += MAKEFILE_TARGET % {'package': package,
                                   'dependency_string': dependency_string}
  return makefile
  
  
def main():
  if len(sys.argv) < 2:
    print('Usage: %s <AUR package>*' % sys.argv[0])
    return 1

  dependency_cache = RosDependencyCache()
  for arg in sys.argv[1:]:
    dependency_cache.add_package_directory(arg)

  print(generate_makefile(dependency_cache))


if __name__ == '__main__':
  main()
