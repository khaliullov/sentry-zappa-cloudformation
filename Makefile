mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir  := $(patsubst %/,%,$(dir $(mkfile_path)))
build_dir   := $(mkfile_dir)

VIRTUALENV  := $(shell which virtualenv 2>/dev/null || echo virtualenv)

.PHONY: all
all:
	@echo "make deploy - deploy Sentry for first time"
	@echo "make update - update Sentry deployments next times"
	@echo "make undeploy - undeploy Sentry from AWS"
	@echo "make certify - update certificates for Sentry"
	@echo "make status - current deployment status"
	@echo "make upgrade - run migrations (in case of Sentry version update)"
	@echo "make tail - tail zappa/AWS Lambda logs"

$(build_dir)/env:
	$(VIRTUALENV) $(build_dir)/env
	$(build_dir)/env/bin/pip install -r $(mkfile_dir)/requirements.txt
	# workaround for AWS Lambda:
	sed -i.bak -e \
	    "s/if content_encoding == 'gzip':/if content_encoding == 'gzip' and data[0] != b'{':/" \
	    -e \
	    "s/if content_encoding == 'deflate':/if content_encoding == 'deflate' and data[0] != b'{':/" \
	    $(build_dir)/env/lib/python2.7/site-packages/sentry/coreapi.py
	# workaround to use Lambda's IAM Role to access S3
	sed -i.bak -e \
	    "s/aws_access_key_id=/# aws_access_key_id=/" \
	    -e \
	    "s/aws_secret_access_key=/# aws_secret_access_key=/" \
	    $(build_dir)/env/lib/python2.7/site-packages/sentry/filestore/s3.py

.PHONY: status deploy undeploy tail certify update
status deploy undeploy tail certify update: $(build_dir)/env
	. $(build_dir)/env/bin/activate; \
	$(build_dir)/env/bin/zappa $@ master

.PHONY: loaddata upgrade
loaddata upgrade: $(build_dir)/env
	. $(build_dir)/env/bin/activate; \
	$(build_dir)/env/bin/zappa invoke master manage.$@
