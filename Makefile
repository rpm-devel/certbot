SPEC        := SPEC/certbot.spec
SPECNAME    := $(shell rpmspec -q --srpm --queryformat '%{name}' $(SPEC) 2>/dev/null)
VERSION     := $(shell rpmspec -q --srpm --queryformat '%{version}' $(SPEC) 2>/dev/null)
RELEASE     := $(shell rpmspec -q --srpm --queryformat '%{release}' $(SPEC) 2>/dev/null)

RPMBUILD    ?= rpmbuild
SPECTOOL    ?= spectool
MOCK        ?= mock

RPMBUILD_DIR ?= $(HOME)/rpmbuild
SOURCES_DIR  := $(RPMBUILD_DIR)/SOURCES
SRPMS_DIR    := $(RPMBUILD_DIR)/SRPMS
RPMS_DIR     := $(RPMBUILD_DIR)/RPMS

.PHONY: all srpm rpm sources clean help

all: rpm

## Download all Source: tarballs declared in the spec
sources:
	@mkdir -p $(SOURCES_DIR)
	$(SPECTOOL) -g -S $(SPEC) -C $(SOURCES_DIR)

## Build SRPM only
srpm: sources
	$(RPMBUILD) -bs $(SPEC)

## Build binary RPM (requires build deps installed)
rpm: sources
	$(RPMBUILD) -ba $(SPEC)

## Build using mock (clean chroot — recommended)
mock-el9: srpm
	$(MOCK) -r almalinux-9-x86_64 --rebuild $(SRPMS_DIR)/certbot-$(VERSION)-$(RELEASE).src.rpm

mock-el10: srpm
	$(MOCK) -r almalinux-10-x86_64 --rebuild $(SRPMS_DIR)/certbot-$(VERSION)-$(RELEASE).src.rpm

mock-fedora: srpm
	$(MOCK) -r fedora-rawhide-x86_64 --rebuild $(SRPMS_DIR)/certbot-$(VERSION)-$(RELEASE).src.rpm

## Clean rpmbuild artifacts
clean:
	rm -f $(SOURCES_DIR)/certbot*.tar.gz $(SOURCES_DIR)/acme*.tar.gz
	rm -f $(SRPMS_DIR)/certbot-$(VERSION)*.src.rpm

help:
	@echo "Targets: sources  srpm  rpm  mock-el9  mock-el10  mock-fedora  clean"
