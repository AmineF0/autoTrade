import { Float, Text } from '@react-three/drei';
import * as THREE from 'three';

interface SensorNodeProps {
  sensor: any;
  position: THREE.Vector3;
}

export function SensorNode({ sensor, position }: SensorNodeProps) {
  const getSensorColor = () => {
    const value = sensor.statistics.average;
    if (value > sensor.metadata.upper) return new THREE.Color(0xff4444);
    if (value < sensor.metadata.lower) return new THREE.Color(0xff8844);
    return new THREE.Color(0x44ff44);
  };

  return (
    <group position={position}>
      <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
        <mesh castShadow>
          <sphereGeometry args={[0.3, 16, 16]} />
          <meshPhysicalMaterial
            color={getSensorColor()}
            roughness={0.1}
            metalness={0.8}
            emissive={getSensorColor()}
            emissiveIntensity={0.4}
          />
        </mesh>
        <Text
          position={[0, 0.5, 0]}
          fontSize={0.3}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {sensor.metadata.name}
        </Text>
      </Float>
    </group>
  );
}