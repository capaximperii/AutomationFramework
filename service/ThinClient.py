from __future__ import division
import hashlib
import json
import math
import os
from datetime import datetime
from TestCase import TestCase
from SuperReport import *

KNOWN_CLIENTS = {}


## keep a js here just in case needed to alter report in future, replace this
javascript = """
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js"></script>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/jquery-throttle-debounce/1.1/jquery.ba-throttle-debounce.min.js"></script>
    <script src="js/jquery.stickyheader.js"></script>
<!-- CSS goes in the document HEAD or added to your external stylesheet -->
<style type="text/css">
table {
    border-collapse: collapse;
    margin-bottom: 3em;
    width: 100%;
    background: #fff;
}
td, th {
    padding: 0.75em 1.5em;
    text-align: left;
}
    td.err {
        background-color: #e992b9;
        color: #fff;
        font-size: 0.75em;
        text-align: center;
        line-height: 1;
    }
th {
    background-color: #31bc86;
    font-weight: bold;
    color: #fff;
    white-space: nowrap;
}
tbody th {
    background-color: #2ea879;
}
tbody tr:nth-child(2n-1) {
    background-color: #f5f5f5;
    transition: all .125s ease-in-out;
}
tbody tr:hover {
    background-color: rgba(129,208,177,.3);
}

/* For appearance */
.sticky-wrap {
    overflow-x: auto;
    overflow-y: hidden;
    position: relative;
    margin: 3em 0;
    width: 100%;
}
.sticky-wrap .sticky-thead,
.sticky-wrap .sticky-col,
.sticky-wrap .sticky-intersect {
    opacity: 0;
    position: absolute;
    top: 0;
    left: 0;
    transition: all .125s ease-in-out;
    z-index: 50;
    width: auto; /* Prevent table from stretching to full size */
}
    .sticky-wrap .sticky-thead {
        box-shadow: 0 0.25em 0.1em -0.1em rgba(0,0,0,.125);
        z-index: 100;
        width: 100%; /* Force stretch */
    }
    .sticky-wrap .sticky-intersect {
        opacity: 1;
        z-index: 150;

    }
        .sticky-wrap .sticky-intersect th {
            background-color: #666;
            color: #eee;
        }
.sticky-wrap td,
.sticky-wrap th {
    box-sizing: border-box;
}

/* Not needed for sticky header/column functionality */
td.user-name {
    text-transform: capitalize;
}
.sticky-wrap.overflow-y {
    overflow-y: auto;
    max-height: 50vh;
}
</style>
<script>

setTimeout(function(){
   window.location.reload(1);
}, 30000);

$(document).ready(function(){
    $("table[id^='report_'] tr:odd").addClass("odd");
    $("table[id^='report_'] tr:not(.odd)").hide();
    $("table[id^='report_'] tr:first-child").show();

    $("table[id^='report_'] tr.odd").click(function(){
        $(this).next("tr").toggle();
        $(this).find(".arrow").toggleClass("up");
    });
});

$(function(){
    $('table').each(function() {
        if($(this).find('thead').length > 0 && $(this).find('th').length > 0) {
            // Clone <thead>
            var $w       = $(window),
                $t       = $(this),
                $thead = $t.find('thead').clone(),
                $col   = $t.find('thead, tbody').clone();

            // Add class, remove margins, reset width and wrap table
            $t
            .addClass('sticky-enabled')
            .css({
                margin: 0,
                width: '100%'
            }).wrap('<div class="sticky-wrap" />');

            if($t.hasClass('overflow-y')) $t.removeClass('overflow-y').parent().addClass('overflow-y');

            // Create new sticky table head (basic)
            $t.after('<table class="sticky-thead" />');

            // If <tbody> contains <th>, then we create sticky column and intersect (advanced)
            if($t.find('tbody th').length > 0) {
                $t.after('<table class="sticky-col" /><table class="sticky-intersect" />');
            }

            // Create shorthand for things
            var $stickyHead  = $(this).siblings('.sticky-thead'),
                $stickyCol   = $(this).siblings('.sticky-col'),
                $stickyInsct = $(this).siblings('.sticky-intersect'),
                $stickyWrap  = $(this).parent('.sticky-wrap');

            $stickyHead.append($thead);

            $stickyCol
            .append($col)
                .find('thead th:gt(0)').remove()
                .end()
                .find('tbody td').remove();

            $stickyInsct.html('<thead><tr><th>'+$t.find('thead th:first-child').html()+'</th></tr></thead>');

            // Set widths
            var setWidths = function () {
                    $t
                    .find('thead th').each(function (i) {
                        $stickyHead.find('th').eq(i).width($(this).width());
                    })
                    .end()
                    .find('tr').each(function (i) {
                        $stickyCol.find('tr').eq(i).height($(this).height());
                    });

                    // Set width of sticky table head
                    $stickyHead.width($t.width());

                    // Set width of sticky table col
                    $stickyCol.find('th').add($stickyInsct.find('th')).width($t.find('thead th').width())
                },
                repositionStickyHead = function () {
                    // Return value of calculated allowance
                    var allowance = calcAllowance();

                    // Check if wrapper parent is overflowing along the y-axis
                    if($t.height() > $stickyWrap.height()) {
                        // If it is overflowing (advanced layout)
                        // Position sticky header based on wrapper scrollTop()
                        if($stickyWrap.scrollTop() > 0) {
                            // When top of wrapping parent is out of view
                            $stickyHead.add($stickyInsct).css({
                                opacity: 1,
                                top: $stickyWrap.scrollTop()
                            });
                        } else {
                            // When top of wrapping parent is in view
                            $stickyHead.add($stickyInsct).css({
                                opacity: 0,
                                top: 0
                            });
                        }
                    } else {
                        // If it is not overflowing (basic layout)
                        // Position sticky header based on viewport scrollTop
                        if($w.scrollTop() > $t.offset().top && $w.scrollTop() < $t.offset().top + $t.outerHeight() - allowance) {
                            // When top of viewport is in the table itself
                            $stickyHead.add($stickyInsct).css({
                                opacity: 1,
                                top: $w.scrollTop() - $t.offset().top
                            });
                        } else {
                            // When top of viewport is above or below table
                            $stickyHead.add($stickyInsct).css({
                                opacity: 0,
                                top: 0
                            });
                        }
                    }
                },
                repositionStickyCol = function () {
                    if($stickyWrap.scrollLeft() > 0) {
                        // When left of wrapping parent is out of view
                        $stickyCol.add($stickyInsct).css({
                            opacity: 1,
                            left: $stickyWrap.scrollLeft()
                        });
                    } else {
                        // When left of wrapping parent is in view
                        $stickyCol
                        .css({ opacity: 0 })
                        .add($stickyInsct).css({ left: 0 });
                    }
                },
                calcAllowance = function () {
                    var a = 0;
                    // Calculate allowance
                    $t.find('tbody tr:lt(3)').each(function () {
                        a += $(this).height();
                    });

                    // Set fail safe limit (last three row might be too tall)
                    // Set arbitrary limit at 0.25 of viewport height, or you can use an arbitrary pixel value
                    if(a > $w.height()*0.25) {
                        a = $w.height()*0.25;
                    }

                    // Add the height of sticky header
                    a += $stickyHead.height();
                    return a;
                };

            setWidths();

            $t.parent('.sticky-wrap').scroll($.throttle(250, function() {
                repositionStickyHead();
                repositionStickyCol();
            }));

            $w
            .load(setWidths)
            .resize($.debounce(250, function () {
                setWidths();
                repositionStickyHead();
                repositionStickyCol();
            }))
            .scroll($.throttle(250, repositionStickyHead));
        }
    });
});
</script>
"""

class ThinClient:
    """
    Constructor  for notional representation of each client
    """
    def __init__(self, address):
        self.configPath = os.path.join("config", "default.ini")
        self.address = address
        self.testsuite   = self.loadConfig()
        self.completed   = []
        self.lastseen = str(datetime.now()).split('.')[0]
        self.template = os.path.join("service","html","template.html")
        self.html = os.path.join("html",address + ".html")
        self.superreport = ""
    """
    Returns the percentage of completion of test cases per client.
    """
    def progress(self):
        if len(self.testsuite) == 0:
            return 100;
        done =  math.floor((len(self.completed) / len(self.testsuite)) * 100)
        return done
    """
    Send the next text case to be executed in order of rank.
    """
    def sendTestCase(self):
        if self.progress() == 100:
            return "QuitAgent"
        test = self.testsuite[len(self.completed)]
        print "sending",test.name,"to",self.address
        timenow = str(datetime.now()).split('.')[0]
        self.lastseen = timenow
        test.starttime = timenow
        test.result = "Running"
        serialize = json.dumps(test, default=lambda o: o.__dict__)
        return serialize
    """
    Receive the result of the last test case sent.
    """
    def recieveResult(self, result, dependency=False):
        if (len(self.testsuite) > len(self.completed)):
            test = self.testsuite[len(self.completed)]
            if dependency:
                (test.result, test.console, test.details) = ("Pass", "Remaining commands in this TestCase ignored.", "")
            else:
                (test.result, test.console, test.details) = json.loads(result)
            print ("\nCompleted " + test.desc + " with result: " + test.console + " and evaluated " + test.result)
            timenow = str(datetime.now()).split('.')[0]
            test.endtime = timenow
            self.lastseen = timenow
            self.completed.append(test)
            #assert( len(self.result) == len(self.completed) )
        else:
            print "discarding rogue result " + str(result)
    """
    Receive the test log file.
    """
    def recieveLog(self, ClientLog):
        unserialized = json.loads(ClientLog)
        timenow = str(datetime.now()).split('.')[0]
        logName = ("thinclient-" + self.address + "-" + timenow + ".log").replace(":","-")
        if not os.path.exists("logs"):
            os.mkdir("logs")
        logPath = os.path.join("logs", logName)
        f = open(logPath, "w")
        f.write(unserialized)
        f.close()
    """
    Receive raw data to include in the report file.
    """
    def recieveInfoToRaw(self, Info, rawtag, separator=":"):
        unserialized = json.loads(Info)
        report = SuperReport(rawtag ,rawtag, separator, unserialized)
        self.superreport = report.dataToBuffer(self.superreport, False)
    """
    Receive data and format into table for the report file.
    """
    def recieveInfoToFmt(self, Info, fmttag, separator=":"):
        unserialized = json.loads(Info)
        report = SuperReport(fmttag, fmttag, separator, unserialized)
        report.formatHtmlTable()
        self.superreport = report.dataToBuffer(self.superreport, True)
    """
    Receive CPU information of the client.
    """
    def recieveCpuInfo(self, CpuInfo):
        unserialized = json.loads(CpuInfo)
        report = CpuReport("__CPUINFOFMT__", "__CPUINFORAW__", ":", unserialized)
        report.formatHtmlTable()
        self.superreport = report.dataToBuffer(self.superreport, True)
        self.superreport = report.dataToBuffer(self.superreport, False)
    """
    Reset the client information from the previous run if it exists.
    """
    def reset(self):
        if(os.path.exists(self.html)):
            os.unlink(self.html)
        if not os.path.exists(os.path.dirname(self.html)):
            os.makedirs(os.path.dirname(self.html))
        f = open(self.template)
        lines = f.readlines()
        self.superreport = "".join(lines)
        f.close()
    """
    Repeat tests specified by a rank range.
    """
    def repeatTests(self, fromrank, torank, times):
        startindex = 0
        stopindex = 0
        testsuitedup = self.loadConfig()
        for test in testsuitedup:
            if test.rank < fromrank:
                startindex +=1
        for test in testsuitedup:
            if test.rank <= torank:
                stopindex +=1
        repeatlist = testsuitedup[startindex:stopindex] * times
        self.testsuite.extend(repeatlist)
        result = json.dumps(("Pass", "Tests repeat added", "Repeating tests clears logs."))
        self.recieveResult(result)
    """
    Skip test cases specified by ranks.
    """
    def deleteTests(self, fromrank, torank):
        startindex = 0
        stopindex = 0
        for test in self.testsuite:
            if test.rank < fromrank:
                startindex +=1
        for test in self.testsuite:
            if test.rank <= torank:
                stopindex +=1
        for i in reversed(range(startindex, stopindex)):
            if (self.testsuite[i].result == "Pending"):
                print "deleting", self.testsuite[i].name
                del self.testsuite[i]

        result = json.dumps(("Pass", "Tests skipped", "Skipping tests clears log"))
        self.recieveResult(result)
    """
    Load configuration file for specific client from disk.
    """
    def loadConfig(self):
        for r in range(0,4):
            stars = ".*" * r
            fname = self.address.rsplit(".", r)[0] + stars + ".ini"
            if os.path.exists(os.path.join("config", fname)):
                self.configPath = os.path.join("config", fname)
                break
        print "Loading %s for client %s" %(self.configPath, self.address)
        return TestCase.LoadFromDisk(self.configPath)
    """
    Compute UUID for the client.
    """
    @staticmethod
    def ComputeClientID(client):
        md5 = hashlib.md5()
        md5.update(client)
        return md5.hexdigest()
    """
    Return the rank of the currently running test case.
    """
    def GetCurrentTestRank(self):
        cur = 0
        # all test case finished, send 'infinity'
        if len(self.testsuite) == len(self.completed):
            cur = 10000
        # none completed, send 'minus infinity'
        elif len(self.completed) == 0:
            cur = -10000
        else :
            cur = self.testsuite[len(self.completed)].rank
        return cur
    """
    Output test information for the stats page.
    """
    def prettyOutput(self):
        p = self.progress()
        #o = javascript
        o = "\n<table border=1 id='report_" + self.address + "' width='100%'>"
        o += "\n<thead><th>Test name</th><th>Description</th><th>Commands list</th><th>Start time</th><th>End at</th><th>Misc information</th><th>Status</th></thead>\n<tbody>"
        for test in self.testsuite:
            o += "\n" + test.prettyOutput()
        o += "\n</tbody>\n"
        o += "<tfoot><tr><th colspan='6'>Completed %s</th><th>%s%%</th></tr></tfoot>" %(self.address, p)
        o += "</table>\n"
        return o
    """
    Format test cases into a html output report.
    """
    def recieveTestInfo(self):
        html = ""
        for test in self.testsuite:
            if test.result == "Pass":
                html += green_img
                html += """<td><img class="resultimg" id="passed"/></td><td class="label">%s</td><td style="background-color: #0f0">PASSED</td><td/>%s<td></test></tr>""" %(test.name, test.console)
            else:
                html += red_img
                html += """<td><img class="resultimg" id="failed"/></td><td class="label">%s</td><td style="background-color: #f00">FAILED</td><td/>%s<td></test></tr>""" %(test.name, test.console)
        return html
    """
    End the processing for this client and generate report.
    """
    def close(self):
        print "Closing client"
        testtable = self.recieveTestInfo()
        self.superreport = self.superreport.replace("__TESTSUITE__", testtable)
        self.superreport = self.superreport.replace("__IPADDR__", self.address)
        now = str(datetime.now()).split(".")[0]
        self.superreport = self.superreport.replace("__DATE__", now)
        SuperReport.dataToFile(self.superreport, self.html)

    """

    """
    def isZombie(self):
        if len(self.completed) == len(self.testsuite):
            return False
        elif self.getTimeSinceLastSeen() > 120 and self.testsuite[len(self.completed)].result == 'Pending':
            return True
        return False
    """
    """
    def getTimeSinceLastSeen(self):
        now = datetime.now()
        lastseen = datetime.strptime(self.lastseen, '%Y-%m-%d %H:%M:%S')
        seconds = (now - lastseen).total_seconds()
        return seconds
    """
    Destructor of object.
    """
    def __del__(self):
        pass
