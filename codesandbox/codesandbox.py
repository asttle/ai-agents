from smolagents import CodeAgent, HfApiModel, SecurityConfig
from smolagents.security import (
    SandboxRestrictedImports, 
    ResourceLimits,
    NetworkPolicy
)

# Define strict security configuration
security_config = SecurityConfig(
    # Limit imports to only essential, safe libraries
    allowed_imports=SandboxRestrictedImports(
        whitelist=[
            'math', 
            'json', 
            'datetime', 
            'typing', 
            're',
            'base64',
        ],
        blacklist=[
            'os', 
            'sys', 
            'subprocess', 
            'socket', 
            'threading', 
            'multiprocessing'
        ]
    ),
    
    # Set resource constraints to prevent abuse
    resource_limits=ResourceLimits(
        max_execution_time=60,  # 60 seconds max execution
        max_memory_mb=256,      # 256MB memory limit
        max_cpu_cores=2,        # Limit to 2 CPU cores
        max_disk_storage_mb=100 # 100MB disk storage limit
    ),
    
    # Configure network policy to restrict external access
    network_policy=NetworkPolicy(
        allow_outbound=False,  # Disable external network access
        allowed_domains=[],    # No domains allowed
        allow_local_network=False  # Prevent local network access
    )
)

# Configure the CodeAgent with enhanced security settings
agent = CodeAgent(
    tools=[],
    model=HfApiModel(
        model_id="deepseek-ai/DeepSeek-R1",
        provider="together",
        max_tokens=8096
    ),
    executor_type="e2b",
    security_config=security_config,
    
    # Additional security parameters
    sandboxing_mode="isolated",  # Completely isolated execution environment
    logging_level="secure",       # Enhanced logging for security monitoring
    error_handling="sanitized"    # Sanitize error messages to prevent information leakage
)
