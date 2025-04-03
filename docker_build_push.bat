@echo off

:: Get the current date and time for versioning
for /f "tokens=2 delims==" %%I in ('"wmic os get localdatetime /value | findstr LocalDateTime"') do set datetime=%%I

:: Format the version as year.month.day.hour
set VERSION=%datetime:~0,4%.%datetime:~4,2%.%datetime:~6,2%.%datetime:~8,2%

:: Build the Docker image with the versioned tag
docker build -t jarebear/pineland-cabinets:%VERSION% .

:: Tag the Docker image as "latest"
docker tag jarebear/pineland-cabinets:%VERSION% jarebear/pineland-cabinets:latest

:: Push both the versioned tag and the "latest" tag
docker push jarebear/pineland-cabinets:%VERSION%
docker push jarebear/pineland-cabinets:latest
