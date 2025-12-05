import logging
import sys
import time
from threading import Thread
from monitors.quality_monitor import QualityMonitor
from config.settings import MONITORING_PORT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class DataQualityService:
    def __init__(self):
        self.quality_monitor = QualityMonitor()
        self.running = False
    
    def start_monitoring(self):
        """Start quality monitoring loop"""
        self.running = True
        logger.info("Data Quality Service started")
        
        while self.running:
            try:
                # Generate quality report every 60 seconds
                summary = self.quality_monitor.get_quality_summary()
                
                # Log alerts if any
                if summary['alerts']:
                    for alert in summary['alerts']:
                        logger.warning(f"Quality Alert: {alert['message']}")
                
                # Log summary stats
                overall = summary['overall']
                logger.info(f"Quality Summary - Total: {overall['total_records']}, "
                          f"Valid: {overall['validity_rate']:.3f}, "
                          f"Avg Score: {overall['avg_quality_score']:.3f}")
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in quality monitoring: {e}")
                time.sleep(10)
    
    def stop(self):
        """Stop the service"""
        self.running = False
        logger.info("Data Quality Service stopped")

def main():
    """Main entry point"""
    service = DataQualityService()
    
    try:
        # Start monitoring in background thread
        monitor_thread = Thread(target=service.start_monitoring, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        service.stop()
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()