#!/bin/bash
brightnessctl g | awk '{print int($1/255*100)}'

