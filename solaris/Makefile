# Copyright 2021, Guillermo Adrián Molina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Use GNU MAKE!!!!!!!!!!!!!!!!
# prerequisite:
# __version__ can not be X.X.dev?, it should be a release
# zfs_clone_manager.egg-info should exist, use:
#   pip install -e <path_to_sources>
# Change IPS_* variables to suit your needs
# usage:
# $ cd /repository/ips-src
# $ gmake -C <path_to_sources>/solaris 
# $ gmake -C <path_to_sources>/solaris publish

# To install the ips package:
# $ sudo pkg install -g $IPS_REPOSITORY_URL zfs-clone-manager-37

PYV=37
PYVER=3.7

IPS_REPOSITORY_URL=http://pkg.gestio.sys/oracle/solaris/
IPS_LOCAL_REPOSITORY_PATH=/repository/base
IPS_LOCAL_REPOSITORY_PUBLISHER=base

COMPONENT_NAME=zfs-clone-manager-$(PYV)

MAKEFILE_PATH=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PROJECT_PATH=$(realpath $(MAKEFILE_PATH)/..)

LINT_CACHE_PATH=$(PWD)/lint-cache
BUILD_DIR=$(PWD)/$(COMPONENT_NAME)
ROOT_PATH=$(BUILD_DIR)/proto_install
BIN_PATH=$(ROOT_PATH)/usr/bin
LIB_PATH=$(ROOT_PATH)/usr/lib
PYTHON_PATH=$(LIB_PATH)/python$(PYVER)
PYTHON_MODULE_PATH=$(PYTHON_PATH)/vendor-packages

PYTHON_SOURCES_PATH=$(PROJECT_PATH)/zcm
PYTHON_SOURCES=$(shell find $(PYTHON_SOURCES_PATH) -name '*.py' -type f)
PYTHON_SOURCES_PATHS=$(shell find $(PYTHON_SOURCES_PATH) -type d ! -name __pycache__)
PYTHON_TARGETS=$(PYTHON_SOURCES:$(PROJECT_PATH)/%=$(PYTHON_MODULE_PATH)/%) 
PYTHON_TARGETS_PATHS=$(PYTHON_SOURCES_PATHS:$(PROJECT_PATH)/%=$(PYTHON_MODULE_PATH)/%)

EGG_SOURCES_PATH=$(PROJECT_PATH)/zfs_clone_manager.egg-info
EGG_SOURCES=$(shell find $(EGG_SOURCES_PATH) -type f)
EGG_TARGETS=$(EGG_SOURCES:$(PROJECT_PATH)/%=$(PYTHON_MODULE_PATH)/%) 
EGG_TARGETS_PATHS=$(EGG_SOURCES_PATH:$(PROJECT_PATH)/%=$(PYTHON_MODULE_PATH)/%)

TARGETS=$(BIN_PATH)/zcm $(PYTHON_TARGETS) $(EGG_TARGETS)
TARGETS_PATHS=$(PYTHON_TARGETS_PATHS) $(EGG_TARGETS_PATHS) $(BIN_PATH)
PACKAGE_RES=$(BUILD_DIR)/$(COMPONENT_NAME).p5m.3.res

include $(PYTHON_SOURCES_PATH)/version.py
	
all: $(TARGETS_PATHS) $(TARGETS) $(PACKAGE_RES)

$(TARGETS_PATHS): 
	mkdir -p $@

$(BIN_PATH)/zcm: $(MAKEFILE_PATH)/zcm
	cp $(MAKEFILE_PATH)/zcm $(BIN_PATH)/zcm

$(PYTHON_TARGETS): $(addprefix $(PYTHON_MODULE_PATH), %) : $(addprefix $(PROJECT_PATH),%)
	cp $< $@

$(EGG_TARGETS): $(addprefix $(PYTHON_MODULE_PATH), %) : $(addprefix $(PROJECT_PATH),%)
	cp $< $@

$(BUILD_DIR)/$(COMPONENT_NAME).p5m.1: $(TARGETS)
	pkgsend generate $(ROOT_PATH) | pkgfmt > $@

$(BUILD_DIR)/$(COMPONENT_NAME).p5m.2: $(BUILD_DIR)/$(COMPONENT_NAME).p5m.1 $(MAKEFILE_PATH)/$(COMPONENT_NAME).mog
	pkgmogrify -D COMPONENT_VERSION=$(__version__) $^ | pkgfmt > $@

$(BUILD_DIR)/$(COMPONENT_NAME).p5m.3: $(BUILD_DIR)/$(COMPONENT_NAME).p5m.2
	pkgdepend generate -md $(ROOT_PATH) $< > $@

$(PACKAGE_RES): $(BUILD_DIR)/$(COMPONENT_NAME).p5m.3
	pkgdepend resolve -m $<
	pkglint -c $(LINT_CACHE_PATH) -r $(IPS_REPOSITORY_URL) $@ || touch $<

publish: $(PACKAGE_RES) $(TARGETS) $(PROJECT_PATH)/LICENSE
	pkgsend publish -d $(ROOT_PATH) -d $(PROJECT_PATH) -s $(IPS_LOCAL_REPOSITORY_PATH) $<
	pkgrepo refresh -p $(IPS_LOCAL_REPOSITORY_PUBLISHER) -s $(IPS_LOCAL_REPOSITORY_PATH)
	svcadm restart application/pkg/server:default

remove:
	pkgrepo remove -s $(IPS_LOCAL_REPOSITORY_PATH) $(COMPONENT_NAME)

clean:
	rm -rf  $(BUILD_DIR)