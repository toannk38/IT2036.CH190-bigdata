import logging
import sys
import time
from datetime import datetime
from tests.pipeline_integration_test import PipelineIntegrationTest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for Pipeline Validation Service"""
    logger.info("Starting Pipeline Validation Service - Phase 2.6")
    
    try:
        # Run comprehensive pipeline validation
        test_runner = PipelineIntegrationTest()
        results = test_runner.run_comprehensive_test()
        
        # Log results
        logger.info(f"Pipeline validation completed")
        logger.info(f"Overall success: {results['overall_success']}")
        logger.info(f"Success rate: {results['success_rate']:.1%}")
        logger.info(f"Checkpoint 1 status: {results['checkpoint_1_status']}")
        
        # Exit with appropriate code
        if results['checkpoint_1_status'] == 'PASSED':
            logger.info("✅ Checkpoint 1 PASSED - Data pipeline fully functional")
            sys.exit(0)
        else:
            logger.error("❌ Checkpoint 1 FAILED - Pipeline validation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()