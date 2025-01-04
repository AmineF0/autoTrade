import { useState, useRef } from 'react';
import { Text, Billboard, Float } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface DepartmentProps {
  name: string;
  position: [number, number, number];
  sensors: [string, any][];
  isHovered: boolean;
  isSelected: boolean;
  onHover: () => void;
  onUnhover: () => void;
  onSelect: () => void;
}

export function Department({
  name,
  position,
  sensors,
  isHovered,
  isSelected,
  onHover,
  onUnhover,
  onSelect,
}: DepartmentProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const targetScale = useRef(1);
  const targetY = useRef(0);

  useFrame((_, delta) => {
    if (meshRef.current) {
      targetScale.current = isHovered || isSelected ? 1.1 : 1;
      targetY.current = isHovered || isSelected ? 1 : 0;
      
      meshRef.current.scale.lerp(
        new THREE.Vector3(targetScale.current, targetScale.current, targetScale.current),
        delta * 5
      );
      meshRef.current.position.y = THREE.MathUtils.lerp(
        meshRef.current.position.y,
        position[1] + targetY.current,
        delta * 5
      );
    }
  });

  const getStatusColor = (sensor: any) => {
    const value = sensor.statistics.average;
    if (value > sensor.metadata.upper) return new THREE.Color(0xff4444);
    if (value < sensor.metadata.lower) return new THREE.Color(0xff8844);
    return new THREE.Color(0x44ff44);
  };

  const getDepartmentColor = () => {
    const colors = sensors.map(([_, sensor]) => getStatusColor(sensor));
    const worstStatus = colors.find(color => color.equals(new THREE.Color(0xff4444)));
    if (worstStatus) return new THREE.Color(0xff4444);
    const warningStatus = colors.find(color => color.equals(new THREE.Color(0xff8844)));
    if (warningStatus) return new THREE.Color(0xff8844);
    return new THREE.Color(0x44ff44);
  };

  const departmentSize = Math.max(4, Math.min(8, sensors.length));

  return (
    <group position={position}>
      <Float speed={1} rotationIntensity={0.1} floatIntensity={0.2}>
        <mesh
          ref={meshRef}
          onClick={onSelect}
          onPointerEnter={onHover}
          onPointerLeave={onUnhover}
          castShadow
          receiveShadow
        >
          <boxGeometry args={[departmentSize, departmentSize, departmentSize]} />
          <meshPhysicalMaterial
            color={getDepartmentColor()}
            transparent
            opacity={0.9}
            roughness={0.2}
            metalness={0.8}
            envMapIntensity={1}
            emissive={getDepartmentColor()}
            emissiveIntensity={isSelected ? 0.4 : 0}
          />
        </mesh>

        <Billboard
          follow={true}
          lockX={false}
          lockY={false}
          lockZ={false}
        >
          <Text
            position={[0, departmentSize + 1, 0]}
            fontSize={1.5}
            outlineWidth={0.2}
            outlineColor="#000000"
            color="white"
            anchorX="center"
            anchorY="middle"
          >
            {name}
          </Text>
        </Billboard>

        {isSelected && (
          <group position={[0, departmentSize / 2, 0]}>
            {sensors.map(([id, sensor], index) => {
              const angle = (index * Math.PI * 2) / sensors.length;
              const radius = departmentSize * 1.5;
              const sensorPosition: [number, number, number] = [
                Math.cos(angle) * radius,
                0,
                Math.sin(angle) * radius,
              ];

              return (
                <group key={id} position={sensorPosition}>
                  <Float speed={3} rotationIntensity={0.2} floatIntensity={0.5}>
                    <mesh castShadow>
                      <sphereGeometry args={[0.8, 32, 32]} />
                      <meshPhysicalMaterial
                        color={getStatusColor(sensor)}
                        roughness={0.1}
                        metalness={0.8}
                        emissive={getStatusColor(sensor)}
                        emissiveIntensity={0.4}
                      />
                    </mesh>
                    <Billboard>
                      <Text
                        position={[0, 1.2, 0]}
                        fontSize={0.8}
                        outlineWidth={0.1}
                        outlineColor="#000000"
                        color="white"
                        anchorX="center"
                        anchorY="middle"
                      >
                        {sensor.metadata.name}
                      </Text>
                    </Billboard>
                  </Float>
                </group>
              );
            })}
          </group>
        )}
      </Float>
    </group>
  );
}