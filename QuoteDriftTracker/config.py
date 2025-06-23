"""
Configuration management for the Jupiter Quote Tracker
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration class for quote tracking parameters"""
    
    # Token configuration
    input_mint: str = 'So11111111111111111111111111111111111111112'  # SOL (wrapped SOL)
    output_mint: str = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'  # USDC
    amount: int = 1000000  # 1 SOL in lamports
    
    # Request configuration
    frequency: float = 5.0  # Requests per second
    duration: int = 60  # Test duration in seconds
    concurrent_requests: int = 10  # Number of concurrent workers
    
    # Trading configuration
    slippage_bps: int = 50  # Slippage in basis points (0.5%)
    
    # Testing configuration
    latency_injection: float = 0.0  # Artificial latency in seconds
    
    # Output configuration
    output_file: str = 'quote_analysis.csv'
    
    # API configuration
    api_timeout: float = 10.0  # API timeout in seconds
    max_retries: int = 3  # Maximum retry attempts
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.frequency <= 0:
            raise ValueError("Frequency must be greater than 0")
            
        if self.duration <= 0:
            raise ValueError("Duration must be greater than 0")
            
        if self.concurrent_requests <= 0:
            raise ValueError("Concurrent requests must be greater than 0")
            
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")
            
        if self.slippage_bps < 0:
            raise ValueError("Slippage BPS cannot be negative")
            
        if self.latency_injection < 0:
            raise ValueError("Latency injection cannot be negative")
    
    @property
    def requests_per_worker(self) -> float:
        """Calculate requests per worker per second"""
        return self.frequency / self.concurrent_requests
    
    @property
    def total_expected_requests(self) -> int:
        """Calculate total expected requests"""
        return int(self.frequency * self.duration)
    
    @property
    def worker_interval(self) -> float:
        """Calculate interval between requests for each worker"""
        return 1.0 / self.requests_per_worker
    
    def get_token_display_name(self, mint_address: str) -> str:
        """Get display name for common token addresses"""
        token_map = {
            'So11111111111111111111111111111111111111112': 'SOL',
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v': 'USDC',
            'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB': 'USDT',
            'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So': 'mSOL',
            'bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1': 'bSOL',
            'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
            '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs': 'ETH',
            'A9mUU4qviSctJVPJdBJWkb28deg915LYJKrzQ19ji3FM': 'USDCet',
        }
        
        return token_map.get(mint_address, mint_address[:8] + '...')
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'input_mint': self.input_mint,
            'input_token': self.get_token_display_name(self.input_mint),
            'output_mint': self.output_mint,
            'output_token': self.get_token_display_name(self.output_mint),
            'amount': self.amount,
            'frequency': self.frequency,
            'duration': self.duration,
            'concurrent_requests': self.concurrent_requests,
            'slippage_bps': self.slippage_bps,
            'latency_injection': self.latency_injection,
            'output_file': self.output_file,
            'total_expected_requests': self.total_expected_requests,
            'requests_per_worker': self.requests_per_worker,
            'worker_interval': self.worker_interval,
        }
    
    def validate_token_addresses(self) -> bool:
        """Validate that token addresses are valid Solana addresses"""
        def is_valid_address(address: str) -> bool:
            try:
                # Basic validation: Solana addresses are base58 encoded and 32-44 characters
                if len(address) < 32 or len(address) > 44:
                    return False
                
                # Check if it contains only valid base58 characters
                valid_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
                return all(c in valid_chars for c in address)
            except:
                return False
        
        return (is_valid_address(self.input_mint) and 
                is_valid_address(self.output_mint) and 
                self.input_mint != self.output_mint)

# Common token configurations
COMMON_TOKENS = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'USDT': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    'mSOL': 'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
    'bSOL': 'bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'ETH': '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
}

# Preset configurations for common trading pairs
PRESET_CONFIGS = {
    'SOL_USDC': {
        'input_mint': COMMON_TOKENS['SOL'],
        'output_mint': COMMON_TOKENS['USDC'],
        'amount': 1000000,  # 1 SOL
    },
    'USDC_SOL': {
        'input_mint': COMMON_TOKENS['USDC'],
        'output_mint': COMMON_TOKENS['SOL'],
        'amount': 100000000,  # 100 USDC
    },
    'SOL_mSOL': {
        'input_mint': COMMON_TOKENS['SOL'],
        'output_mint': COMMON_TOKENS['mSOL'],
        'amount': 1000000,  # 1 SOL
    },
    'mSOL_SOL': {
        'input_mint': COMMON_TOKENS['mSOL'],
        'output_mint': COMMON_TOKENS['SOL'],
        'amount': 1000000,  # 1 mSOL
    },
}
