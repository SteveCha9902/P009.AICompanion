@echo off
chcp 65001 > nul

title P009.AICompanion - Comprehensive Test Suite

echo ======================================================================
echo    P009.AICompanion System Comprehensive Test Runner
echo    (Sprint 36 Behavioral + Sprint 37 Growth + Sprint 38 Agency)
echo ======================================================================
echo.

set "BASE_DIR=%~dp0"
set "BACKEND_DIR=%BASE_DIR%backend"
set "MOBILE_DIR=%BASE_DIR%mobile"
set "OVERALL_STATUS=SUCCESS"

:: ----------------------------------------------------------------------
:: 1. Backend Pytest Suite Execution
:: ----------------------------------------------------------------------
echo [STEP 1/2] Running Backend Core Engine Test Suite (55 Tests)...
echo ----------------------------------------------------------------------

cd /d "%BACKEND_DIR%"
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at backend\.venv
    set "OVERALL_STATUS=FAILED"
    goto :MOBILE_CHECK
)

.venv\Scripts\python.exe -m pytest tests/test_unified_companion_brain.py tests/test_situation_understanding_engine.py tests/test_adaptive_self_improvement_engine.py tests/test_companion_observability_engine.py tests/test_constitutional_governance_engine.py tests/test_trust_and_safety_layer.py tests/test_identity_continuity_engine.py tests/test_companion_autonomy_engine.py tests/test_life_goals_future_planning_engine.py tests/test_life_timeline_engine.py tests/test_relationship_evolution_engine.py tests/test_personality_consistency_engine.py tests/test_companion_cognitive_os.py tests/test_emotionally_adaptive_companion_engine.py tests/test_proactive_companion_engine.py tests/test_relationship_memory_engine.py tests/test_shared_reality_joint_attention.py tests/test_visual_awareness_perception_engine.py tests/test_voice_identity_speech_engine.py tests/test_production_avatar_release.py tests/test_motion_variety_engine.py tests/test_emotion_relationship_embodiment.py tests/test_embodied_behavior_engine.py tests/test_lip_sync_engine.py tests/test_face_engine.py tests/test_avatar_asset_pipeline.py tests/test_avatar_behavior_sync_engine.py tests/test_character_agency_engine.py tests/test_character_growth_and_relationship_dynamics.py tests/test_behavioral_personality_engine.py tests/test_reflection_engine.py tests/test_dynamic_personality_behavior.py tests/test_character_behavior.py tests/test_autobiographical_memory.py tests/test_relationship_evolution.py tests/test_character_identity.py tests/test_personality_consistency.py tests/test_character_agency.py tests/test_persona_integrity.py tests/test_backend_integration.py



























if errorlevel 1 (
    echo.
    echo [FAIL] Backend Pytest Suite encountered errors.
    set "OVERALL_STATUS=FAILED"
) else (
    echo.
    echo [PASS] Backend Pytest Suite 100 Percent Passed.
)

:: ----------------------------------------------------------------------
:: 2. Mobile TypeScript Verification
:: ----------------------------------------------------------------------
:MOBILE_CHECK
echo.
echo ======================================================================
echo [STEP 2/2] Running Mobile TypeScript Compilation Check...
echo ----------------------------------------------------------------------

cd /d "%MOBILE_DIR%"
call npx.cmd tsc --noEmit
if errorlevel 1 (
    echo.
    echo [FAIL] Mobile TypeScript compilation errors found.
    set "OVERALL_STATUS=FAILED"
) else (
    echo.
    echo [PASS] Mobile TypeScript verification passed with 0 Errors.
)

:: ----------------------------------------------------------------------
:: Final Summary
:: ----------------------------------------------------------------------
echo.
echo ======================================================================
if "%OVERALL_STATUS%"=="SUCCESS" (
    echo  [ALL TESTS PASSED] P009.AICompanion is fully verified and stable.
) else (
    echo  [TEST SUITE FAILED] One or more tests failed. Check logs above.
)
echo ======================================================================
echo.

cd /d "%BASE_DIR%"
if not "%1"=="--no-pause" (
    pause
)
