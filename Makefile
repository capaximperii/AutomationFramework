SHELL:=/bin/bash
LOGLOCATION:=service/storage/logs
server:
	@mkdir -p ${LOGLOCATION}
	@python service/AutomationServer.py > >(tee ${LOGLOCATION}/serverlog.txt) 2> >(tee ${LOGLOCATION}/serverlog.txt >&2)

client:
	@python agent/AutomationAgent.py test --debug

shell:
	@python agent/cliStart.py shell

ncurses:
	@python agent/cliStart.py ncurses

recap:
	@python agent/cliStart.py file /tmp/automation-history.log

clean:
	@echo "Removing py bytecode release and log files."
	@rm -f $$(find . -name *.pyc)
	@rm -rf service/storage
	@rm -rf release
	@rm -rf logs
	@rm -rf html
	@rm -rf tmp

package: clean
	@mkdir -p release
	@rm -f release/server.tgz
	tar zcf release/server.tgz config service agent/cli/bin/sanity.py
	@rm -f release/agent.tgz
	tar zcf release/agent.tgz agent
	@echo server.tgz and agent.tgz packaged for release

#Reminder: Update checksum whenever selenium is updated in source of this file: sanity.py
sanity: clean dos2unix permissions
	@echo "Checking dependencies and python packages needed..."
	@python -B agent/cli/bin/sanity.py
	@echo "Unless sanity reported a dependency error, you are good to run!"

dos2unix:
	@echo Convert all line endings to unix like
	@for i in $$(find . -type f) ; do dos2unix $$i >/dev/null 2>&1; done

permissions:
	@echo Removing executable permissions from files that do not need it
	@chmod 600 Makefile >/dev/null 2>&1
	@for i in $$(find service -type f -executable -not -name "*.so") ; do chmod 600 $$i ; >/dev/null 2>&1; done
	@for i in $$(find agent/ -type f -executable -not -name "*.so") ; do chmod 600 $$i ; >/dev/null 2>&1; done
	@for i in $$(find config/ -type f -executable -not -name "*.so") ; do chmod 600 $$i ; >/dev/null 2>&1; done
	@for i in $$(find agent/cli/bin -type f) ; do chmod u+x $$i ; >/dev/null 2>&1; done

