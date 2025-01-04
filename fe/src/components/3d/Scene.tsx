import { useRef } from 'react';
import { OrbitControls, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';

interface SceneProps {
  children: React.ReactNode;
  cameraTarget: THREE.Vector3;
}

export function Scene({ children, cameraTarget }: SceneProps) {
  const lightRef = useRef<THREE.DirectionalLight>(null);
  const controlsRef = useRef<any>(null);
  const { camera } = useThree();

  return (
    <>
      <color attach="background" args={['#1a1a1a']} />
      <Environment preset="warehouse" />
      
      <ambientLight intensity={0.8} />
      <directionalLight
        ref={lightRef}
        position={[20, 20, 20]}
        intensity={2}
        castShadow
        shadow-mapSize={[2048, 2048]}
      />
      
      <OrbitControls 
        ref={controlsRef}
        target={cameraTarget}
        enableDamping={true}
        dampingFactor={0.05}
        minDistance={10}
        maxDistance={50}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.5}
      />
      
      {children}
    </>
  );
}