#!/bin/bash

if [ "$APP_ENV" = "development" ]; then
  exec npm run dev
else
  exec serve -s build
fi
