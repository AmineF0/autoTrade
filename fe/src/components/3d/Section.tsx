import { useRef, useMemo } from 'react';
import { Text, Float } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { SensorNode } from './SensorNode';

interface SectionProps {
  sectionNumber: string;
  position: THREE.Vector3;
  size: THREE.Vector3;
  sensors: any[];
  isHovered: boolean;
  isSelected: boolean;
  onHover: () => void;
  onUnhover: () => void;
  onSelect: () => void;
}

export function Section({
  sectionNumber,
  position,
  size,
  sensors,
  isHovered,
  isSelected,
  onHover,
  onUnhover,
  onSelect,
}: SectionProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const targetScale = useRef(new THREE.Vector3(1, 1, 1));

  const sectionColor = useMemo(() => {
    const hasAlert = sensors.some(sensor => {
      const value = sensor.statistics.average;
      return value > sensor.metadata.upper || value < sensor.metadata.lower;
    });
    return hasAlert ? new THREE.Color(0xff4444) : new THREE.Color(0x44ff44);
  }, [sensors]);

  useFrame((_, delta) => {
    if (meshRef.current) {
      const scale = isHovered || isSelected ? 1.02 : 1;
      targetScale.current.set(scale, scale, scale);
      meshRef.current.scale.lerp(targetScale.current, delta * 5);
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={onSelect}
        onPointerEnter={onHover}
        onPointerLeave={onUnhover}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[size.x, size.y, size.z]} />
        <meshPhysicalMaterial
          color={sectionColor}
          transparent
          opacity={0.6}
          roughness={0.2}
          metalness={0.3}
          envMapIntensity={1}
          emissive={sectionColor}
          emissiveIntensity={isSelected ? 0.3 : isHovered ? 0.2 : 0}
        />
      </mesh>

      <Float speed={1} rotationIntensity={0.1} floatIntensity={0.2}>
        <Text
          position={[0, size.y / 2 + 0.5, 0]}
          fontSize={0.8}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {`Section ${sectionNumber}`}
        </Text>
      </Float>

      {isSelected && sensors.map((sensor, index) => {
        const angle = (index * Math.PI * 2) / sensors.length;
        const radius = Math.min(size.x, size.z) * 0.4;
        const sensorPosition = new THREE.Vector3(
          Math.cos(angle) * radius,
          0,
          Math.sin(angle) * radius
        );

        return (
          <SensorNode
            key={sensor.id}
            sensor={sensor}
            position={sensorPosition}
          />
        );
      })}
    </group>
  );
}