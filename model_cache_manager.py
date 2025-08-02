"""
Model Cache Manager for Guardian AI
Provides intelligent caching and cleanup for downloaded models
"""

import os
import time
import json
import shutil
import stat
from datetime import datetime, timedelta


class ModelCacheManager:
    def __init__(self, cache_dir=".guardian_cache", max_age_days=7):
        """
        Initialize model cache manager

        Args:
            cache_dir: Directory to store cached models
            max_age_days: Maximum age of cached models before refresh
        """
        self.cache_dir = cache_dir
        self.max_age_days = max_age_days
        self.cache_info_file = os.path.join(cache_dir, "cache_info.json")

        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache_info(self):
        """Get cache information from file"""
        if os.path.exists(self.cache_info_file):
            try:
                with open(self.cache_info_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def update_cache_info(self, model_type, download_time=None):
        """Update cache information"""
        cache_info = self.get_cache_info()
        if download_time is None:
            download_time = datetime.now().isoformat()

        cache_info[model_type] = {
            "downloaded_at": download_time,
            "last_accessed": datetime.now().isoformat(),
        }

        with open(self.cache_info_file, "w") as f:
            json.dump(cache_info, f, indent=2)

    def is_cache_valid(self, model_type, model_path):
        """Check if cached model is still valid"""
        # Check if model directory exists and has required files
        if not os.path.exists(model_path) or not os.path.exists(
            os.path.join(model_path, "config.json")
        ):
            return False

        # Check cache age
        cache_info = self.get_cache_info()
        if model_type not in cache_info:
            return False

        download_time = datetime.fromisoformat(cache_info[model_type]["downloaded_at"])
        age_limit = datetime.now() - timedelta(days=self.max_age_days)

        return download_time > age_limit

    def get_model_path(self, model_type):
        """Get the path for a specific model type"""
        return os.path.join(self.cache_dir, f"{model_type}_models")

    def mark_accessed(self, model_type):
        """Mark model as recently accessed"""
        cache_info = self.get_cache_info()
        if model_type in cache_info:
            cache_info[model_type]["last_accessed"] = datetime.now().isoformat()
            with open(self.cache_info_file, "w") as f:
                json.dump(cache_info, f, indent=2)

    def cleanup_old_cache(self):
        """Remove old cached models"""
        cache_info = self.get_cache_info()
        age_limit = datetime.now() - timedelta(days=self.max_age_days)

        for model_type, info in cache_info.items():
            download_time = datetime.fromisoformat(info["downloaded_at"])
            if download_time < age_limit:
                model_path = self.get_model_path(model_type)
                if os.path.exists(model_path):
                    print(f"Removing old cached {model_type} models...")
                    shutil.rmtree(model_path)

                # Remove from cache info
                del cache_info[model_type]

        # Update cache info file
        with open(self.cache_info_file, "w") as f:
            json.dump(cache_info, f, indent=2)

    def clear_all_cache(self):
        """Clear all cached models"""
        if os.path.exists(self.cache_dir):
            print("Clearing all cached models...")
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _handle_remove_readonly(self, func, path, exc):
        """Handle read-only files on Windows"""
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)

    def _force_remove_directory(self, directory):
        """Force remove directory even with read-only files (Windows compatible)"""
        if not os.path.exists(directory):
            return True

        try:
            # Try normal removal first
            shutil.rmtree(directory)
            return True
        except PermissionError:
            try:
                # Handle read-only files on Windows
                shutil.rmtree(directory, onerror=self._handle_remove_readonly)
                return True
            except Exception as e:
                print(f"⚠️ Warning: Could not remove {directory}: {e}")
                return False

    def cleanup_temp_directories(self):
        """Clean up any leftover temporary directories"""
        temp_dirs = ["temp_repo", "temp_repo_images"]
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                if self._force_remove_directory(temp_dir):
                    print(f"🧹 Cleaned up leftover temporary directory: {temp_dir}")
                else:
                    print(
                        f"⚠️ Could not fully clean up {temp_dir} - some files may remain"
                    )

    def get_cache_stats(self):
        """Get cache statistics"""
        cache_info = self.get_cache_info()
        stats = {
            "cache_directory": self.cache_dir,
            "total_models": len(cache_info),
            "models": {},
        }

        for model_type, info in cache_info.items():
            model_path = self.get_model_path(model_type)
            size_mb = 0
            if os.path.exists(model_path):
                size_mb = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(model_path)
                    for filename in filenames
                ) / (1024 * 1024)

            stats["models"][model_type] = {
                "downloaded_at": info["downloaded_at"],
                "last_accessed": info["last_accessed"],
                "size_mb": round(size_mb, 2),
                "path": model_path,
            }

        return stats


# Global cache manager instance
cache_manager = ModelCacheManager()


def print_cache_stats():
    """Print cache statistics"""
    stats = cache_manager.get_cache_stats()
    print("\n📊 Model Cache Statistics:")
    print(f"Cache Directory: {stats['cache_directory']}")
    print(f"Total Models: {stats['total_models']}")

    for model_type, info in stats["models"].items():
        print(f"\n{model_type.title()} Models:")
        print(f"  Downloaded: {info['downloaded_at']}")
        print(f"  Last Accessed: {info['last_accessed']}")
        print(f"  Size: {info['size_mb']} MB")
        print(f"  Path: {info['path']}")


if __name__ == "__main__":
    print_cache_stats()
