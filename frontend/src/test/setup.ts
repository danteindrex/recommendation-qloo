import '@testing-library/jest-dom';

// Mock Three.js WebGL context
Object.defineProperty(window, 'WebGLRenderingContext', {
  value: function() {
    return {
      canvas: document.createElement('canvas'),
      drawingBufferWidth: 1024,
      drawingBufferHeight: 768,
      getParameter: () => 'WebGL',
      getExtension: () => null,
      createShader: () => ({}),
      shaderSource: () => {},
      compileShader: () => {},
      createProgram: () => ({}),
      attachShader: () => {},
      linkProgram: () => {},
      useProgram: () => {},
      createBuffer: () => ({}),
      bindBuffer: () => {},
      bufferData: () => {},
      enableVertexAttribArray: () => {},
      vertexAttribPointer: () => {},
      drawArrays: () => {},
      clear: () => {},
      clearColor: () => {},
      enable: () => {},
      disable: () => {},
      depthFunc: () => {},
      blendFunc: () => {},
      viewport: () => {}
    };
  }
});

// Mock WebGL2RenderingContext
Object.defineProperty(window, 'WebGL2RenderingContext', {
  value: window.WebGLRenderingContext
});

// Mock HTMLCanvasElement.getContext
HTMLCanvasElement.prototype.getContext = function(contextId: string) {
  if (contextId === 'webgl' || contextId === 'webgl2') {
    return new (window as any).WebGLRenderingContext();
  }
  return null;
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock performance.now for animations
Object.defineProperty(window, 'performance', {
  value: {
    now: () => Date.now()
  }
});

// Mock requestAnimationFrame
global.requestAnimationFrame = (callback: FrameRequestCallback) => {
  return setTimeout(callback, 16);
};

global.cancelAnimationFrame = (id: number) => {
  clearTimeout(id);
};