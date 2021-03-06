from ..fsGetNumberDescription import fsGetNumberDescription;
from mWindowsAPI import oSystemInfo;

def fbUpdateReportForNULLPointer(
  oCdbWrapper, oBugReport, oProcess, oThread, sViolationTypeId, uAccessViolationAddress, sViolationTypeDescription, oVirtualAllocation
):
  if uAccessViolationAddress == 0:
    sOffset = "";
  elif uAccessViolationAddress < oSystemInfo.uAllocationAddressGranularity:
    sOffset = "+%s" % fsGetNumberDescription(uAccessViolationAddress, "+");
  else:
    uAccessViolationNegativeOffset = {"x86": 1 << 32, "x64": 1 << 64}[oProcess.sISA] - uAccessViolationAddress;
    if uAccessViolationNegativeOffset >= oSystemInfo.uAllocationAddressGranularity:
      return False;
    sOffset = "-%s" % fsGetNumberDescription(uAccessViolationNegativeOffset, "-");
  oBugReport.sBugTypeId = "AV%s@NULL%s" % (sViolationTypeId, sOffset);
  oBugReport.sBugDescription = "Access violation while %s memory at 0x%X using a NULL pointer." % \
      (sViolationTypeDescription, uAccessViolationAddress);
  oBugReport.sSecurityImpact = None;
  # You normally cannot allocate memory at address 0, so it is impossible for an exploit to avoid this exception.
  # Therefore there is no collateral bug handling.
  return True;
