import pcbnew

board = pcbnew.GetBoard()
if not isinstance(board, pcbnew.BOARD):
    raise RuntimeError("No usable BOARD object. Ensure you're running this from the PCB Editor after opening a .kicad_pcb file.")

netinfo = board.GetNetInfo()

def get_pads_on_net(net_name):
    """
    Get all pads on a specific net
    Returns a list of dictionaries with necessary data
    """
    pads_data = []
    
    for footprint in board.GetFootprints():
        component_ref = footprint.GetReference()
        
        for pad in footprint.Pads():
            if pad.GetNetname() == net_name:
                pad_info = {
                    'position': pad.GetCenter(),          # Pad center coordinates
                    'component_ref': component_ref,       # LED1, LED2, etc.
                    'pad_number': pad.GetNumber(),        # "1" or "2"
                    'footprint': footprint               # The footprint object (for routing)
                }
                
                pads_data.append(pad_info)
    
    return pads_data

def add_track(start, end, layer=pcbnew.F_Cu):
    """
    Add a track between two points
    """
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(int(0.25 * 1e6))  # 0.25mm track width
    track.SetLayer(layer)
    board.Add(track)
    return track

def add_vertical_horizontal(nets_dict, x_tolerance_mm=0.1, y_range_mm=2.5, x_range_mm = 2.5, y_tolerance_mm=0.1, diagonal_x_tolerance_mm = 3, diagonal_y_tolerance_mm = 2):
    x_v = int(x_tolerance_mm * 1e6)  # X alignment tolerance (still 0.05mm)
    y_v = int(y_range_mm * 1e6)      # Y proximity limit (now 2.5mm)
    x_h = int(x_range_mm * 1e6)
    y_h = int (y_tolerance_mm * 1e6)
    
    diag_x = int(diagonal_x_tolerance_mm * 1e6)
    diag_y = int(diagonal_y_tolerance_mm * 1e6)

    connected = set()

    for net_name, pads in nets_dict.items():
        print(f"Processing net: {net_name}")

        for i in range(len(pads)):
            for j in range(i + 1, len(pads)):
                pad1 = pads[i]
                pad2 = pads[j]

                if pad1['component_ref'] == pad2['component_ref']:
                    continue  # Don't connect pads within the same footprint

                x1, y1 = pad1['position'].x, pad1['position'].y
                x2, y2 = pad2['position'].x, pad2['position'].y
                
                key = tuple(sorted([
                        pad1['component_ref'] + pad1['pad_number'],
                        pad2['component_ref'] + pad2['pad_number']
                    ]))
                if key in connected:
                    continue

                if (abs(x1 - x2) <= x_v and abs(y1 - y2) <= y_v) or (abs(x1 - x2) <= x_h and abs(y1-y2) <= y_h):
    
                    connected.add(key)

                    add_track(pad1['position'], pad2['position'])

                    print(f"  Connected {pad1['component_ref']} (pad {pad1['pad_number']}) ↕ {pad2['component_ref']} (pad {pad2['pad_number']})")
                    
                #if (abs(x1 - x2) <= diag_x and abs(y1 - y2) <= y_h):
                    
                #    connected.add(key)
                    
                #    add_track   
    


def clear_tracks_by_width(width_mm):
    """
    Delete tracks with specific width (useful if you used a specific width for scripted tracks)
    """
    tracks_to_remove = []
    width_iu = int(width_mm * 1e6)  # Convert to internal units
    
    for track in board.GetTracks():
        if track.GetWidth() == width_iu:
            tracks_to_remove.append(track)
    
    for track in tracks_to_remove:
        board.Remove(track)
    
    print(f"Removed {len(tracks_to_remove)} tracks with width {width_mm}mm")
    pcbnew.Refresh()

# Build dictionary of all nets and their pads
nets_dict = {}

for net_code in range(netinfo.GetNetCount()):
    net = netinfo.GetNetItem(net_code)
    net_name = net.GetNetname()
    
    if net_name == '':
        continue 
    
    net_info = get_pads_on_net(net_name)
    
    if net_info:  # Only add nets that have pads
        nets_dict[net_name] = net_info

# Need some print statement to see if the dict is populated
add_vertical_horizontal(nets_dict)

#clear_tracks_by_width(0.25) # for clearing


# Command Line Commands
# exec(open("C:\Users\mukka\Downloads\message.py").read())
# pcbnew.Refresh()