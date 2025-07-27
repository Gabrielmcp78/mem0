#!/usr/bin/env python3
"""
Production Memory System Setup
Complete setup for local memory ecosystem with all components
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from memory_config_manager import MemoryConfigManager

class ProductionMemorySetup:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.config_manager = MemoryConfigManager()
        self.setup_steps = []
    
    def log_step(self, step: str, status: str = "INFO"):
        """Log setup step"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{symbols.get(status, 'ℹ️')} {step}")
        self.setup_steps.append({"step": step, "status": status})
    
    def run_command(self, command: list, description: str, check_output: bool = False):
        """Run command with error handling"""
        try:
            self.log_step(f"Running: {description}")
            if check_output:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                return result.stdout
            else:
                subprocess.run(command, check=True)
            self.log_step(f"Completed: {description}", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log_step(f"Failed: {description} - {e}", "ERROR")
            return False
    
    def check_prerequisites(self):
        """Check all prerequisites"""
        self.log_step("Checking prerequisites...")
        
        prerequisites = {
            'docker': ['docker', '--version'],
            'docker-compose': ['docker-compose', '--version'],
            'python3': ['python3', '--version'],
            'pip': ['pip', '--version'],
            'ollama': ['ollama', '--version']
        }
        
        missing = []
        for tool, command in prerequisites.items():
            if not self.run_command(command, f"Checking {tool}", check_output=True):
                missing.append(tool)
        
        if missing:
            self.log_step(f"Missing prerequisites: {', '.join(missing)}", "ERROR")
            return False
        
        self.log_step("All prerequisites found", "SUCCESS")
        return True
    
    def setup_python_environment(self):
        """Setup Python virtual environment and dependencies"""
        self.log_step("Setting up Python environment...")
        
        # Create virtual environment
        if not (self.base_dir / 'venv').exists():
            if not self.run_command([sys.executable, '-m', 'venv', 'venv'], "Creating virtual environment"):
                return False
        
        # Activate and install dependencies
        pip_path = self.base_dir / 'venv' / 'bin' / 'pip'
        python_path = self.base_dir / 'venv' / 'bin' / 'python'
        
        # Install mem0 with all extras
        if not self.run_command([str(pip_path), 'install', '-e', '.[graph]'], "Installing mem0 with graph support"):
            return False
        
        # Install additional dependencies
        additional_deps = [
            'pyyaml',
            'requests',
            'asyncio',
            'autogen-agentchat',
            'crewai',
            'langchain',
            'docker-compose'
        ]
        
        for dep in additional_deps:
            if not self.run_command([str(pip_path), 'install', dep], f"Installing {dep}"):
                self.log_step(f"Warning: Failed to install {dep}", "WARNING")
        
        self.log_step("Python environment setup complete", "SUCCESS")
        return True
    
    def setup_ollama(self):
        """Setup Ollama with required models"""
        self.log_step("Setting up Ollama...")
        
        # Check if Ollama is running
        try:
            subprocess.run(['pgrep', '-f', 'ollama serve'], check=True, capture_output=True)
            self.log_step("Ollama already running", "SUCCESS")
        except subprocess.CalledProcessError:
            self.log_step("Starting Ollama service...")
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5)
        
        # Pull required models
        models = ['llama3.2:3b', 'nomic-embed-text']
        for model in models:
            if not self.run_command(['ollama', 'pull', model], f"Pulling {model}"):
                self.log_step(f"Warning: Failed to pull {model}", "WARNING")
        
        self.log_step("Ollama setup complete", "SUCCESS")
        return True
    
    def setup_directories(self):
        """Create necessary directories"""
        self.log_step("Creating directories...")
        
        directories = [
            'data/qdrant',
            'data/neo4j/data',
            'data/neo4j/logs',
            'data/neo4j/import',
            'data/neo4j/plugins',
            'data/redis',
            'data/postgres',
            'logs'
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.log_step("Directories created", "SUCCESS")
        return True
    
    def setup_configuration(self):
        """Setup configuration files"""
        self.log_step("Setting up configuration...")
        
        # Create default configuration
        self.config_manager.config = self.config_manager.create_default_config()
        self.config_manager.save_config()
        
        # Create OpenMemory .env file
        openmemory_env_path = self.base_dir / 'openmemory' / 'api' / '.env'
        openmemory_env_path.parent.mkdir(parents=True, exist_ok=True)
        
        env_vars = self.config_manager.get_openmemory_env()
        env_content = '\n'.join([f"{key}={value}" for key, value in env_vars.items()])
        openmemory_env_path.write_text(env_content)
        
        # Create docker-compose environment file
        docker_env_path = self.base_dir / '.env'
        docker_env_vars = self.config_manager.get_docker_compose_env()
        docker_env_content = '\n'.join([f"{key}={value}" for key, value in docker_env_vars.items()])
        docker_env_path.write_text(docker_env_content)
        
        self.log_step("Configuration files created", "SUCCESS")
        return True
    
    def start_docker_services(self):
        """Start Docker services"""
        self.log_step("Starting Docker services...")
        
        # Stop any existing services
        self.run_command(['docker-compose', '-f', 'docker-compose.production.yml', 'down'], "Stopping existing services")
        
        # Start services
        if not self.run_command(['docker-compose', '-f', 'docker-compose.production.yml', 'up', '-d'], "Starting Docker services"):
            return False
        
        # Wait for services to be ready
        self.log_step("Waiting for services to be ready...")
        time.sleep(30)
        
        # Check service health
        services_to_check = ['mem0-qdrant', 'mem0-neo4j', 'mem0-redis', 'mem0-postgres']
        for service in services_to_check:
            result = self.run_command(['docker', 'ps', '--filter', f'name={service}', '--format', 'table {{.Names}}\\t{{.Status}}'], f"Checking {service}", check_output=True)
            if service in result and 'Up' in result:
                self.log_step(f"{service} is running", "SUCCESS")
            else:
                self.log_step(f"{service} may not be ready", "WARNING")
        
        return True
    
    def start_mem0_server(self):
        """Start Mem0 API server"""
        self.log_step("Starting Mem0 server...")
        
        python_path = self.base_dir / 'venv' / 'bin' / 'python'
        
        # Start Mem0 server in background
        with open('logs/mem0_server.log', 'w') as log_file:
            process = subprocess.Popen(
                [str(python_path), '-m', 'mem0.server'],
                stdout=log_file,
                stderr=log_file
            )
        
        # Save PID
        with open('mem0_server.pid', 'w') as pid_file:
            pid_file.write(str(process.pid))
        
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            self.log_step(f"Mem0 server started (PID: {process.pid})", "SUCCESS")
            return True
        else:
            self.log_step("Failed to start Mem0 server", "ERROR")
            return False
    
    def run_tests(self):
        """Run comprehensive tests"""
        self.log_step("Running comprehensive tests...")
        
        python_path = self.base_dir / 'venv' / 'bin' / 'python'
        
        # Run test suite
        result = self.run_command([str(python_path), 'test_complete_ecosystem.py'], "Running test suite")
        
        if result:
            self.log_step("All tests passed", "SUCCESS")
        else:
            self.log_step("Some tests failed - check test_results.json", "WARNING")
        
        return result
    
    def create_management_scripts(self):
        """Create management scripts"""
        self.log_step("Creating management scripts...")
        
        # Stop script
        stop_script = """#!/bin/bash
echo "🛑 Stopping Memory Ecosystem..."

# Stop Docker services
docker-compose -f docker-compose.production.yml down

# Stop Mem0 server
if [ -f mem0_server.pid ]; then
    kill $(cat mem0_server.pid) 2>/dev/null || true
    rm mem0_server.pid
fi

# Stop Ollama (optional)
# pkill -f "ollama serve"

echo "✅ Memory Ecosystem stopped"
"""
        
        # Status script
        status_script = """#!/bin/bash
echo "📊 Memory Ecosystem Status"
echo "=========================="

echo "🐳 Docker Services:"
docker-compose -f docker-compose.production.yml ps

echo ""
echo "🤖 Ollama Models:"
ollama list

echo ""
echo "🧠 Mem0 Server:"
if [ -f mem0_server.pid ] && ps -p $(cat mem0_server.pid) > /dev/null; then
    echo "✅ Running (PID: $(cat mem0_server.pid))"
else
    echo "❌ Not running"
fi

echo ""
echo "🌐 Service Endpoints:"
echo "  OpenMemory UI:      http://localhost:13000"
echo "  OpenMemory API:     http://localhost:18765"
echo "  Mem0 Server:        http://localhost:1987"
echo "  Qdrant Dashboard:   http://localhost:16333/dashboard"
echo "  Neo4j Browser:      http://localhost:17474"
echo "  Ollama API:         http://localhost:11434"
"""
        
        # Write scripts
        (self.base_dir / 'stop_memory_ecosystem.sh').write_text(stop_script)
        (self.base_dir / 'status_memory_ecosystem.sh').write_text(status_script)
        
        # Make executable
        os.chmod(self.base_dir / 'stop_memory_ecosystem.sh', 0o755)
        os.chmod(self.base_dir / 'status_memory_ecosystem.sh', 0o755)
        
        self.log_step("Management scripts created", "SUCCESS")
        return True
    
    def print_final_summary(self):
        """Print final setup summary"""
        print("\n" + "🎉" * 20)
        print("PRODUCTION MEMORY ECOSYSTEM READY!")
        print("🎉" * 20)
        
        print("\n📍 ACCESS POINTS:")
        endpoints = [
            ("OpenMemory UI", "http://localhost:13000"),
            ("OpenMemory API", "http://localhost:18765"),
            ("Mem0 Server", "http://localhost:1987"),
            ("Qdrant Dashboard", "http://localhost:16333/dashboard"),
            ("Neo4j Browser", "http://localhost:17474"),
            ("Ollama API", "http://localhost:11434")
        ]
        
        for name, url in endpoints:
            print(f"  {name:<20} {url}")
        
        print("\n🔧 MANAGEMENT:")
        print("  Start:   ./start_memory_ecosystem.sh")
        print("  Stop:    ./stop_memory_ecosystem.sh")
        print("  Status:  ./status_memory_ecosystem.sh")
        print("  Test:    python test_complete_ecosystem.py")
        
        print("\n📚 INTEGRATION FILES:")
        files = [
            "agent_memory_integrations.py - Universal agent integrations",
            "memory_config_manager.py - Configuration management",
            "test_complete_ecosystem.py - Comprehensive testing",
            "memory_config.yaml - System configuration"
        ]
        
        for file_desc in files:
            print(f"  {file_desc}")
        
        print("\n🚀 READY FOR ANY AGENT FRAMEWORK!")
        print("   - AutoGen")
        print("   - CrewAI") 
        print("   - LangChain")
        print("   - Custom Agents")
        
        # Save setup summary
        summary = {
            "setup_completed": True,
            "timestamp": time.time(),
            "endpoints": dict(endpoints),
            "setup_steps": self.setup_steps
        }
        
        with open('setup_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Setup summary saved to setup_summary.json")
    
    def run_complete_setup(self):
        """Run complete production setup"""
        print("🌟 Starting Production Memory Ecosystem Setup")
        print("=" * 60)
        
        setup_functions = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Python Environment", self.setup_python_environment),
            ("Ollama Setup", self.setup_ollama),
            ("Directory Creation", self.setup_directories),
            ("Configuration Setup", self.setup_configuration),
            ("Docker Services", self.start_docker_services),
            ("Mem0 Server", self.start_mem0_server),
            ("Management Scripts", self.create_management_scripts),
            ("System Tests", self.run_tests)
        ]
        
        failed_steps = []
        
        for step_name, step_func in setup_functions:
            print(f"\n{'='*20} {step_name} {'='*20}")
            try:
                if not step_func():
                    failed_steps.append(step_name)
                    self.log_step(f"{step_name} failed", "ERROR")
                else:
                    self.log_step(f"{step_name} completed successfully", "SUCCESS")
            except Exception as e:
                failed_steps.append(step_name)
                self.log_step(f"{step_name} error: {e}", "ERROR")
        
        print("\n" + "=" * 60)
        
        if not failed_steps:
            self.log_step("🎉 COMPLETE SETUP SUCCESSFUL!", "SUCCESS")
            self.print_final_summary()
            return True
        else:
            self.log_step(f"❌ Setup failed at: {', '.join(failed_steps)}", "ERROR")
            print("Check the logs above for details on failed steps.")
            return False

if __name__ == "__main__":
    setup = ProductionMemorySetup()
    success = setup.run_complete_setup()
    sys.exit(0 if success else 1)