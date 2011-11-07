# All rights Glastopf Project and Lukas Rist

import sqlite3


class WebServerBotnetAnalyzer():
    """Simpe tool to analyze the data collected with wesbos"""
    def __init__(self):
        pass
    
    def select_from_db(self):
        """Get the data from the SQLite database"""
        self.db = sqlite3.connect('../db/sqlite.db')
        cursor = self.db.cursor()
        cursor.execute("SELECT id, names FROM CnC")
        return cursor
    
    def handle_data(self, ip_lists):
        """Handle the IP lists containing the drones"""
        total_sum_botnets = 0
        total_sum_active_botnets = 0
        total_sum_inactive_botnets = 0
        total_sum_drones = 0
        
        for data in ip_lists:
            total_sum_botnets += 1
            drone_ips = data[1]
            botnet_id = data[0]
            if drone_ips:
                drones_ip_list = drone_ips.split(",")
                sum_drones = self.handle_drone_ips(botnet_id, drones_ip_list)
                total_sum_drones += sum_drones
                total_sum_active_botnets += 1
            else:
                total_sum_inactive_botnets += 1
        print "Total number of botnets: %s" % total_sum_botnets
        print "Total number of inactive botnets: %s" % total_sum_inactive_botnets
        print "Total number of active botnets: %s" % total_sum_active_botnets        
        print "Total number of drones in all analyzed botnets: %s" % total_sum_drones
        self.db.commit()
        self.db.close()
    
    def handle_drone_ips(self, botnet_id, drone_ips):
        print "Botnet id: %s" % botnet_id
        sum_drones = len(drone_ips)
        print "Number of drones in botnet: %s" % sum_drones
        return sum_drones
    
    def analyze_drones(self):
        drone_lists = self.select_from_db()
        self.handle_data(drone_lists)
    
if __name__ == "__main__":
    analyzer = WebServerBotnetAnalyzer()
    analyzer.analyze_drones()