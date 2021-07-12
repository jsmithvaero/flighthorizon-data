UAFVASFAA=../flighthorizon-data/flight-tests/UAF-VAS-FAA/
TEST1=2021.01.22-01.29.FlightTest1/
TEST2=2021.02.26-03.04.FlightTest2/
TEST3=2021.03.26-04.01.FlightTest3/
TEST4=2021.06.04-06.11.FlightTest4/

TESTUNCLEAR=2021.04.21-04.22/

all: ; python3 runner.py demo-data/

clean: 
	- rm *.png
	- rm -rf 2021-*

# ------------------------- Flight Test Targets --------------------------
# 
# These targets require cloning (with lfs!) of flighthorizon-data at the
# same level as this repository.
# 
# ------------------------------------------------------------------------

# ------------------- FLIGHT TEST 1 (UAF-FAA-VAS 2021) -------------------

test1prep:
	python3 runner.py $(UAFVASFAA)$(TEST1)2021.01.22.PreFlightTest1/

test1day1:
	python3 runner.py $(UAFVASFAA)$(TEST1)2021.01.25.Day1/

test1day2:
	python3 runner.py $(UAFVASFAA)$(TEST1)2021.01.26.Day2/

test1day3:
	python3 runner.py $(UAFVASFAA)$(TEST1)2021.01.27.Day3/

test1day4:
	python3 runner.py $(UAFVASFAA)$(TEST1)2021.01.28.Day4/

test1day5:
	python3 runner.py $(UAFVASFAA)$(TEST1)2021.01.29.Day5/

test1:
	make test1prep test1day1 test1day2 test1day3 test1day4 test1day5

# ------------------- FLIGHT TEST 2 (UAF-FAA-VAS 2021) -------------------

test2day1:
	python3 runner.py $(UAFVASFAA)$(TEST2)2021.03.02.Day1/

test2day2:
	python3 runner.py $(UAFVASFAA)$(TEST2)2021.03.03.Day2/

test2day3:
	python3 runner.py $(UAFVASFAA)$(TEST2)2021.03.04.Day3/

test2:
	make test2day1 test2day2 test2day3

# ------------------- FLIGHT TEST 3 (UAF-FAA-VAS 2021) -------------------

test3day1:
	python3 runner.py $(UAFVASFAA)$(TEST3)2021.04.23.Friday/

test3day2:
	python3 runner.py $(UAFVASFAA)$(TEST3)2021.04.26.Monday/

test3day3:
	python3 runner.py $(UAFVASFAA)$(TEST3)2021.04.27.Tuesday/

test3day4:
	python3 runner.py $(UAFVASFAA)$(TEST3)2021.04.28.Wednesday/

test3day5:
	python3 runner.py $(UAFVASFAA)$(TEST3)2021.04.29.Tuesday/

test3:
	make test3day1 test3day2 test3day3 test3day4 test3day5

# ------------- 2 DAYS NOT CLEARLY BINNED (UAF-FAA-VAS 2021) -------------

testUnclear1:
	python3 runner.py $(UAFVASFAA)$(TESTUNCLEAR)2021.04.21/

testUnclear2:
	python3 runner.py $(UAFVASFAA)$(TESTUNCLEAR)2021.04.22/

testUnclear:
	make testUnclear1 testUnclear2

# ------------------- FLIGHT TEST 4 (UAF-FAA-VAS 2021) -------------------

# TODO
