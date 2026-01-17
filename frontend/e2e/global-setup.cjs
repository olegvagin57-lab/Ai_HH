const { execSync } = require('child_process');
const http = require('http');

/**
 * Wait for backend to be ready
 */
function waitForBackend(maxAttempts = 120, delay = 2000) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    
    const check = () => {
      attempts++;
      if (attempts % 10 === 0) {
        console.log(`Attempt ${attempts}/${maxAttempts}: Checking backend health...`);
      }
      
      const req = http.get('http://127.0.0.1:8000/api/v1/health/ready', (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          if (res.statusCode === 200) {
            console.log('✅ Backend is ready!');
            resolve();
          } else {
            if (attempts >= maxAttempts) {
              reject(new Error(`Backend not ready after ${maxAttempts} attempts (last status: ${res.statusCode})`));
            } else {
              setTimeout(check, delay);
            }
          }
        });
      });
      
      req.on('error', (err) => {
        if (attempts >= maxAttempts) {
          reject(new Error(`Backend not ready after ${maxAttempts} attempts (last error: ${err.message})`));
        } else {
          setTimeout(check, delay);
        }
      });
      
      req.setTimeout(5000, () => {
        req.destroy();
        if (attempts >= maxAttempts) {
          reject(new Error(`Backend not ready after ${maxAttempts} attempts (timeout)`));
        } else {
          setTimeout(check, delay);
        }
      });
    };
    
    check();
  });
}

/**
 * Create test users
 */
async function createTestUsers() {
  console.log('Creating test users...');
  
  try {
    const env = {
      ...process.env,
      MONGODB_URL: process.env.MONGODB_URL || 'mongodb://localhost:27017',
      MONGODB_DATABASE: process.env.MONGODB_DATABASE || 'hh_analyzer_test',
      REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379',
      SECRET_KEY: process.env.SECRET_KEY || 'test-secret-key-for-ci-min-32-chars-required-12345678901234567890',
      ENVIRONMENT: 'test',
    };
    
    execSync(
      'python scripts/wait_and_create_users.py',
      {
        cwd: '../backend',
        env: env,
        stdio: 'inherit'
      }
    );
    
    console.log('✅ Test users created successfully');
  } catch (error) {
    console.error('❌ Error creating test users:', error.message);
    // Don't fail the setup if users already exist
    if (error.message.includes('already exists')) {
      console.log('⚠️  Users already exist, continuing...');
    } else {
      throw error;
    }
  }
}

/**
 * Global setup function
 */
async function globalSetup() {
  console.log('🔧 Running global setup...');
  
  // Wait for backend to be ready
  console.log('⏳ Waiting for backend to be ready...');
  await waitForBackend();
  console.log('✅ Backend is ready');
  
  // Create test users
  await createTestUsers();
  
  console.log('✅ Global setup completed');
}

module.exports = globalSetup;
