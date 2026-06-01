"""Test Pydantic schemas"""
from app.schemas import (
    JobSubmitRequest,
    ScanpyParameters,
    PARAMETER_PRESETS,
)
from pydantic import ValidationError


def test_schemas():
    """Test schema validation"""
    
    print("=" * 60)
    print("SCHEMA VALIDATION TESTS")
    print("=" * 60)
    
    # Test 1: Valid job submission with default preset
    print("\n[1/5] Testing valid job submission with default preset...")
    try:
        request = JobSubmitRequest(
            input_type="mtx",
            input_path="/data/test_data/pbmc_10k",
            preset="default"
        )
        print(f"✓ Valid request created")
        print(f"  Input: {request.input_type}")
        print(f"  Preset: {request.preset}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Test 2: Custom parameters
    print("\n[2/5] Testing custom parameters...")
    try:
        custom_params = ScanpyParameters(
            min_genes=300,
            min_cells=5,
            n_genes_lower=2000,
            n_genes_upper=5500,
            pct_mt_cutoff=5.0
        )
        request = JobSubmitRequest(
            input_type="h5",
            input_path="/data/test.h5",
            preset="custom",
            parameters=custom_params
        )
        print(f"✓ Custom parameters validated")
        print(f"  min_genes: {request.parameters.min_genes}")
        print(f"  n_genes_upper: {request.parameters.n_genes_upper}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Test 3: Invalid input type
    print("\n[3/5] Testing invalid input type (should fail)...")
    try:
        request = JobSubmitRequest(
            input_type="invalid",  # Should fail
            input_path="/data/test",
            preset="default"
        )
        print(f"✗ Should have failed validation!")
        return False
    except ValidationError:
        print(f"✓ Correctly rejected invalid input_type")
    
    # Test 4: Invalid parameter range
    print("\n[4/5] Testing invalid parameter range (should fail)...")
    try:
        params = ScanpyParameters(
            n_genes_lower=5000,
            n_genes_upper=2000  # Lower than n_genes_lower
        )
        print(f"✗ Should have failed validation!")
        return False
    except ValidationError:
        print(f"✓ Correctly rejected invalid gene thresholds")
    
    # Test 5: Parameter presets
    print("\n[5/5] Testing parameter presets...")
    print(f"✓ Available presets: {list(PARAMETER_PRESETS.keys())}")
    default = PARAMETER_PRESETS["default"]
    print(f"  Default min_genes: {default.min_genes}")
    print(f"  Default leiden_resolution: {default.leiden_resolution}")
    stringent = PARAMETER_PRESETS["stringent"]
    print(f"  Stringent min_genes: {stringent.min_genes}")
    print(f"  Stringent leiden_resolution: {stringent.leiden_resolution}")
    
    # Success
    print("\n" + "=" * 60)
    print("✓✓✓ ALL SCHEMA TESTS PASSED ✓✓✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import sys
    success = test_schemas()
    sys.exit(0 if success else 1)