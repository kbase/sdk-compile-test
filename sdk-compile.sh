#!/bin/bash

if [ -f *.spec ] && [ -f Makefile ] ; then
  for f in ./*.spec; do
    kb-sdk compile "$f";
  done
fi
