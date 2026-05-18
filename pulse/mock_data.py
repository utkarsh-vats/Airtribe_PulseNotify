# Mock flight price ranges for Indian domestic routes
# Format: 'ORIGIN-DESTINATION': (min_price, max_price) in INR

MOCK_PRICES = {
    # Delhi hub
    'DEL-BOM': (3000, 7000),
    'DEL-BLR': (4000, 9000),
    'DEL-HYD': (3500, 8000),
    'DEL-MAA': (4000, 8500),
    'DEL-CCU': (3500, 7500),
    'DEL-GOI': (3000, 7000),
    'DEL-JAI': (1500, 4000),
    'DEL-AMD': (2500, 6000),
    'DEL-LKO': (1500, 3500),
    'DEL-PAT': (2000, 5000),
    'DEL-SXR': (3000, 8000),
    'DEL-IXC': (1500, 4000),

    # Mumbai hub
    'BOM-DEL': (3000, 7000),
    'BOM-BLR': (2500, 6000),
    'BOM-HYD': (2500, 5500),
    'BOM-MAA': (3000, 6500),
    'BOM-CCU': (4000, 8500),
    'BOM-GOI': (2000, 5000),
    'BOM-AMD': (1500, 4000),
    'BOM-JAI': (2500, 6000),
    'BOM-PNQ': (1500, 3500),
    'BOM-IDR': (2000, 4500),

    # Bangalore hub
    'BLR-DEL': (4000, 9000),
    'BLR-BOM': (2500, 6000),
    'BLR-HYD': (1500, 4000),
    'BLR-MAA': (1500, 3500),
    'BLR-CCU': (3500, 7500),
    'BLR-GOI': (2000, 5000),
    'BLR-PNQ': (2000, 5000),
    'BLR-COK': (2000, 5000),

    # Hyderabad hub
    'HYD-DEL': (3500, 8000),
    'HYD-BOM': (2500, 5500),
    'HYD-BLR': (1500, 4000),
    'HYD-MAA': (2000, 4500),
    'HYD-CCU': (3500, 7000),
    'HYD-VTZ': (1500, 3500),

    # Chennai hub
    'MAA-DEL': (4000, 8500),
    'MAA-BOM': (3000, 6500),
    'MAA-BLR': (1500, 3500),
    'MAA-HYD': (2000, 4500),
    'MAA-CCU': (3500, 7000),
    'MAA-COK': (2000, 4500),

    # Kolkata hub
    'CCU-DEL': (3500, 7500),
    'CCU-BOM': (4000, 8500),
    'CCU-BLR': (3500, 7500),
    'CCU-HYD': (3500, 7000),
    'CCU-MAA': (3500, 7000),
    'CCU-GAU': (2000, 5000),
    'CCU-IXB': (1500, 3500),
    'CCU-PAT': (1500, 4000),

    # Goa routes
    'GOI-DEL': (3000, 7000),
    'GOI-BOM': (2000, 5000),
    'GOI-BLR': (2000, 5000),

    # Northeast & hill stations
    'DEL-IXA': (4000, 9000),
    'DEL-DMU': (3500, 8000),
    'CCU-GAU': (2000, 5000),
    'DEL-DED': (2000, 5000),
    'DEL-IXJ': (2500, 6000),
}

# IATA code reference
AIRPORT_CODES = {
    'DEL': 'Delhi (Indira Gandhi International)',
    'BOM': 'Mumbai (Chhatrapati Shivaji Maharaj)',
    'BLR': 'Bangalore (Kempegowda International)',
    'HYD': 'Hyderabad (Rajiv Gandhi International)',
    'MAA': 'Chennai (Chennai International)',
    'CCU': 'Kolkata (Netaji Subhas Chandra Bose)',
    'GOI': 'Goa (Manohar International)',
    'JAI': 'Jaipur (Jaipur International)',
    'AMD': 'Ahmedabad (Sardar Vallabhbhai Patel)',
    'LKO': 'Lucknow (Chaudhary Charan Singh)',
    'PAT': 'Patna (Jay Prakash Narayan)',
    'PNQ': 'Pune (Pune Airport)',
    'COK': 'Kochi (Cochin International)',
    'SXR': 'Srinagar (Sheikh ul-Alam International)',
    'IXC': 'Chandigarh (Chandigarh International)',
    'IDR': 'Indore (Devi Ahilyabai Holkar)',
    'VTZ': 'Visakhapatnam (Visakhapatnam Airport)',
    'GAU': 'Guwahati (Lokpriya Gopinath Bordoloi)',
    'IXB': 'Bagdogra (Bagdogra Airport)',
    'IXA': 'Agartala (Maharaja Bir Bikram)',
    'DMU': 'Dimapur (Dimapur Airport)',
    'DED': 'Dehradun (Jolly Grant Airport)',
    'IXJ': 'Jammu (Jammu Airport)',
}