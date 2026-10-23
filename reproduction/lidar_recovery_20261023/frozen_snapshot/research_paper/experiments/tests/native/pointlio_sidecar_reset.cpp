#include "IndicatorSidecar.h"

#include <fstream>
#include <string>

namespace
{
bool add_measurement_frame(std::uint64_t header_ns, std::uint64_t end_ns,
                           const Eigen::Matrix3d &preupdate_rotation)
{
    const std::uint32_t frame_id =
        pointlio_indicator_sidecar.register_input_frame(header_ns);
    pointlio_indicator_sidecar.begin_frame(frame_id, end_ns);
    pointlio_indicator_sidecar.set_frame_stage("MEASUREMENT");
    pointlio_indicator_sidecar.set_expected_groups(1);
    pointlio_indicator_sidecar.begin_group(0, end_ns - 10);
    const Eigen::MatrixXd rows = Eigen::MatrixXd::Identity(6, 6);
    pointlio_indicator_sidecar.capture_group(preupdate_rotation, rows);
    if (!pointlio_indicator_sidecar.finish_group()) return false;
    pointlio_indicator_sidecar.finish_frame();
    return true;
}
}  // namespace

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    const std::string output_dir = argv[1];
    std::string error;
    if (!pointlio_indicator_sidecar.initialize(output_dir, error)) return 3;

    Eigen::Matrix3d preupdate_rotation;
    preupdate_rotation << 0.0, -1.0, 0.0,
                          1.0,  0.0, 0.0,
                          0.0,  0.0, 1.0;
    if (!add_measurement_frame(1000, 1100, preupdate_rotation)) return 4;

    const std::uint32_t reset_frame =
        pointlio_indicator_sidecar.register_input_frame(3000);
    pointlio_indicator_sidecar.begin_frame(reset_frame, 3100);
    pointlio_indicator_sidecar.record_reset(reset_frame, 3100,
                                            "TEST_POST_STARTUP_RESET");

    if (!add_measurement_frame(5000, 5100, preupdate_rotation)) return 5;
    if (!pointlio_indicator_sidecar.flush_pending()) return 6;

    std::ofstream poses(output_dir + "/poses.csv");
    poses << "timestamp_ns,source_frame_id,valid,unavailable_reason,event\n"
          << "1100,1,true,,POSE\n"
          << "3100,2,true,,POSE\n"
          << "5100,3,true,,POSE\n";
    poses.flush();
    return poses ? 0 : 7;
}
