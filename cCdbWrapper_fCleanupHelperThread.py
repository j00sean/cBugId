import time, threading;
from .cBugReport_CdbCouldNotBeTerminated import cBugReport_CdbCouldNotBeTerminated;
from .cBugReport_CdbTerminatedUnexpectedly import cBugReport_CdbTerminatedUnexpectedly;
from mWindowsAPI import *;

def cCdbWrapper_fCleanupHelperThread(oCdbWrapper):
  # wait for debugger thread to terminate.
  oCdbWrapper.oCdbStdInOutHelperThread.fWait();
  oCdbWrapper.fbFireEvent("Log message", "cdb stdin/out closed");
  if not oCdbWrapper.bCdbWasTerminatedOnPurpose:
    if not oCdbWrapper.oCdbConsoleProcess.bIsRunning:
      oBugReport = cBugReport_CdbTerminatedUnexpectedly(oCdbWrapper, oCdbWrapper.oCdbConsoleProcess.uExitCode);
      oBugReport.fReport(oCdbWrapper);
    elif not oCdbWrapper.oCdbConsoleProcess.fbTerminate(5):
      oBugReport = cBugReport_CdbCouldNotBeTerminated(oCdbWrapper);
      oBugReport.fReport(oCdbWrapper);
    else:
      oCdbWrapper.fbFireEvent("Log message", "cdb.exe terminated");
  # wait for stderr thread to terminate.
  oCdbWrapper.oCdbStdErrHelperThread.fWait();
  oCdbWrapper.fbFireEvent("Log message", "cdb stderr closed");
  if oCdbWrapper.bCdbWasTerminatedOnPurpose:
    # Wait for cdb.exe to terminate
    oCdbWrapper.oCdbConsoleProcess.fbWait();
    oCdbWrapper.fbFireEvent("Log message", "cdb.exe terminated");
  # Wait for all other threads to terminate
  while len(oCdbWrapper.aoActiveHelperThreads) > 1:
    for oHelperThread in oCdbWrapper.aoActiveHelperThreads:
      if oHelperThread == oCdbWrapper.oCleanupHelperThread: continue;
      # There is no timeout on this join, so we may hang forever. To be able to analyze such a bug, we will log the
      # details of the thread we are waiting on here:
      oCdbWrapper.fbFireEvent("Log message", "Waiting for thread", {
        "Thread": str(oHelperThread),
      });
      oHelperThread.fWait();
      # The list may have been changed while we waited, so start again.
      break;
  assert (
    len(oCdbWrapper.aoActiveHelperThreads) == 1 \
    and oCdbWrapper.aoActiveHelperThreads[0] == oCdbWrapper.oCleanupHelperThread
  ), \
      "Expected only cleanup helper thread to remain, got %s" % \
      ", ".join([str(oHelperThread) for oHelperThread in oCdbWrapper.aoActiveHelperThreads]);
  # Report that we're finished.
  oCdbWrapper.fbFireEvent("Log message", "Finished");
  oCdbWrapper.fbFireEvent("Finished");
    
