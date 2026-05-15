# PulseNotify

## Overview

PulseNotify is a flight price monitoring backend built with Django DRF, Celery, Redis, and PostgreSQL. Users set price alerts for flight routes; Celery Beat checks prices every 60 seconds and fires async notifications when thresholds are hit.