#!/bin/csh
setenv JAVA_HOME @JAVA_HOME@
setenv PATH ${PATH}:${JAVA_HOME}/bin:${JAVA_HOME}/jre/bin
setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:@JAVA_LD@
