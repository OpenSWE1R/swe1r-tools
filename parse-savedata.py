#!/usr/bin/env python3

import sys
import struct

tournaments = [
  "Amateur Podracing Circuit",
  "Semipro Podracing Circuit",
  "Galactic Podracing Circuit",
  "Invitational Podracing Circuit",
  "<Unused 5>"
]

races = [
  "Boonta Training Course", # 3 laps = 0, best lap = 50 + 0
  "Mon Gazza Speedway", # best lap = 50 + 32
  "Beedo's Wild Ride", # 3 laps = 4, best lap = 50 + 4
  "Aquilaris Classic",
  "Malastare 100",
  "Vengeance",
  "Spice Mine Run",
  "<Unused 7>",

  "Sunken City", # best lap = 50 + 14
  "Howler Gorge", # best lap = 50 + 6
  "Dug Derby",
  "Scrapper's Run",
  "Zugga Challenge",
  "Baroo Coast",
  "Bumpy's Breakers",
  "<Unused 15>",

  "Executioner", # 3 laps = 40, best lap = 50 + 40
  "Sebulba's Legacy",
  "Grabvine Gateway",
  "Andobi Mountain Run",
  "Dethro's Revenge", # best lap = 50 + 20
  "Fire Mountain Rally",
  "The Boonta Classic",
  "<Unused 23>",

  "Ando Prime Centrum",
  "Abyss",
  "The Gauntlet",
  "Inferno", # best lap = 50 + 30
  "<Unused 28>",
  "<Unused 29>",
  "<Unused 30>",
  "<Unused 31>",

  "<Unused 32>",
  "<Unused 33>",
  "<Unused 34>",
  "<Unused 35>",
  "<Unused 36>",
  "<Unused 37>",
  "<Unused 38>",
  "<Unused 39>",
]

#FIXME: This order is from the menu and has not been confirmed yet
podracers = [
  "Anakin Skywalker", # 0 (confirmed)
  "Teemto Pagalies", # 1
  "Sebulba", # 2
  "Ratts Tyerell", # 3
  "Aldar Beedo", # 4
  "Mawhonic", # 5
  "Ark 'Bumpy' Roose", # 6
  "Wan Sandage", # 7
  "Mars Guo", # 8
  "Ebe Endocott", # 9 (confirmed)
  "Dud Bolt", # 10 (confirmed)
  "Gasgano", # 11 (confirmed)
  "Clegg Holdfast", # 12
  "Elan Mak", # 13
  "Neva Kee", # 14 (confirmed)
  "Bozzie Baranta", # 15
  "Boles Roor", # 16
  "Ody Mandrell", # 17
  "Fud Sang",# 18
  "Ben Quadinaros", # 19
  "Slide Paramita", # 20
  "Toy Dampner", # 21
  "\"Bullseye\" Navior", # 22
  "<Unused 23>",
  "<Unused 24>",
  "<Unused 25>",
  "<Unused 26>",
  "<Unused 27>",
  "<Unused 28>",
  "<Unused 29>",
  "<Unused 30>",
  "<Unused 31>"
]

part_types = [
  "Traction",
  "Turning",
  "Acceleration",
  "Top Speed",
  "Air Brake",
  "Cooling",
  "Repair"
]

parts = [
  [
    "R-20 Repulsorgrip",
    "R-60 Repulsorgrip",
    "R-80 Repulsorgrip",
    "R-100 Repulsorgrip",
    "R-300 Repulsorgrip",
    "R-600 Repulsorgrip"
  ],[
    "Control Linkage",
    "Control Shift Plate",
    "Control Vectro-Jet",
    "Control Coupling",
    "Control Nozzle",
    "Control Stabilizer"
  ],[
    "Dual 20 PCX Injector",
    "44 PCX Injector",
    "Dual 32 PCX Injector",
    "Quad 32 PCX Injector",
    "Quad 44 Injector",
    "Mag-6 Injector"
  ],[
    "Plug2 Thrust Coil",
    "Plug3 Thrust Coil",
    "Plug5 Thrust Coil",
    "Plug8 Thrust Coil",
    "Block5 Thrust Coil",
    "Block6 Thrust Coil"
  ],[
    "Mark II Air Brake",
    "Mark III Air Brake",
    "Mark IV Air Brake",
    "Mark V Air Brake",
    "Tri-Jet Air Brake",
    "Quadrijet Air Brake"
  ],[
    "Coolant Radiator",
    "Stack-3 Radiator",
    "Stack-6 Radiator",
    "Rod Coolant Pump",
    "Dual Coolant Pump",
    "Turbo Coolant Pump"
  ],[
    "Single Power Cell",
    "Dual Power Cell",
    "Quad Power Cell",
    "Cluster Power Plug",
    "Rotary Power Plug",
    "Cluster2 Power Plug"
  ]
]

def readString(data):
  return data.rstrip(b'\0').decode('ascii')

def dumpProfile(data):
  name = readString(data[0:32])
  print("Name: '%s'" % (name))

  #FIXME: 0x20
  #FIXME: Profile-index [16 bit] and another 16 bit field
  unk3C = struct.unpack("<I", data[32:36])[0]
  print("Unknown (at 0x20): 0x%08X" % (unk3C))

  last_podracer = data[36]
  print("Last podracer: %d (%s)" % (last_podracer, podracers[last_podracer]))

  for i in range(0, 5):
    print("Tournament %d (%s):" % (i, tournaments[i]))
    for b in range(0, 8):
      index = i * 8 + b
      unlocked = (data[0x25 + i] >> b) & 1
      rank = (data[0x2A + index // 2] >> b) & 3
      ranks = ["1st", "2nd", "3rd", "Not finished"]
      print("- Race %d (%s): %s, %s" % (b, races[index], "Unlocked" if unlocked else "Locked", ranks[rank]))

  print("Podracers:")
  for i in range(0, 4):
    for b in range(0, 8):
      index = i * 8 + b
      unlocked = data[0x34 + i] & (1 << b)
      print("- Podracer %d (%s): %s" % (index, podracers[index], "Unlocked" if unlocked else "Locked"))

  truguts = struct.unpack("<I", data[0x38:0x3C])[0]
  print("Truguts: %u" % (truguts))

  #Padding?
  unk3C = struct.unpack("<I", data[0x3C:0x40])[0]
  assert(unk3C == 0x00000000)

  pit_droids = data[0x40]
  print("Pit droids: %u / 4" % (pit_droids))

  print("Parts:")
  for i in range(0, 7):
    part_level = data[0x41+i]
    part_health = data[0x48+i]
    print("- %s: Level %d (%s); Health: %u / 255" % (part_types[i], part_level, parts[i][part_level], part_health))
  
with open(sys.argv[1], 'rb') as in_file:
  data = in_file.read()
  
  if len(data) == 1408:
    is_console = True # Dreamcast
    print("Non-PC files are not supported at this point")
    sys.exit(1)
  elif len(data) == 4056:
    is_console = False # PC Version
    # FIXME: Assert the header is correct
    data = data[4:]
  elif len(data) == 84:
    data = data[4:]
    dumpProfile(data)
    sys.exit(0)
  else:
    print("Unsure what file this is")
    sys.exit(1)

  for i in range(0, 4):
    print("Tournament %d (%s):" % (i, tournaments[i]))
    for b in range(0, 8):
      index = i * 8 + b
      unlocked = data[0xC + i] & (1 << b)
      print("- Race %d (%s): %s" % (b, races[index], "Unlocked" if unlocked else "Locked"))
    print("")

  print("Podracers:")
  for i in range(0, 4):
    for b in range(0, 8):
      index = i * 8 + b
      unlocked = data[0x10 + i] & (1 << b)
      print("- Podracer %d (%s): %s" % (index, podracers[index], "Unlocked" if unlocked else "Locked"))
  print("")

  # FIXME: Not implemented yet
  for i in range(0, 4):
    print("Profile %d:" % i)
    dumpProfile(data[0x14+i*80:0x14+i*80+80])
    #FIXME: Lots of stuff
    print("")

  times = ["3 Laps", "Best lap"]
  for j in range(0, 2):
    print("Best times (%s):" % (times[j]))
    for i in range(0, 25):

      #FIXME: Note that only even slots are used.
      #       Not sure what the odd ones are used for. 
      o = (j * 25 + i) * 2

      def formatTime(time):
        milliseconds = int(time * 1000)
        seconds = milliseconds // 1000
        minutes = seconds // 60
        return "%02d:%02d.%.03d" % (minutes % 60, seconds % 60, milliseconds % 1000.0)
      time = struct.unpack("<f", data[0x154 + 4 * o:0x154 + 4 * o + 4])[0]
      name = readString(data[0x2E4 + 32 * o:0x2E4 + 32 * o + 32])
      podracer = data[0xF64 + o]

      # There is a 32 bit float time of 3599.99 if the race was not done yet
      bad_time = struct.unpack('f', struct.pack('f', 3599.99))[0]
      if (time >= bad_time):
        printable_time = "--:--.---"
        name = ""
      else:
        printable_time = formatTime(time)

      # FIXME: Race names are bad.
      #        These are the names as the track list from the extract-data tool.
      #        (Sorted by planet)
      race = "Unknown track"

      print("- Time %d: %s, %s '%s' (%d (%s))" % (i, race, printable_time, name, podracer, podracers[podracer]))
    print("")

    # Padding?
    assert(data[0xFC8:0xFD4] == bytes([0] * 12))

