import { Injectable, HttpException, HttpStatus, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config'; // <-- Import ConfigService
import axios, { AxiosError } from 'axios';
import * as process from 'process';

@Injectable()
export class WorkflowService {
  private readonly logger = new Logger(WorkflowService.name);
  private readonly pythonApi: string;

  // Inject ConfigService for professional environment variable management
  constructor(private readonly configService: ConfigService) {
    // Get the AI Engine URL from environment variables
    this.pythonApi = this.configService.get<string>('PYTHON_API_URL') || 'http://localhost:8000';
    this.logger.log(`Using Python AI API at: ${this.pythonApi}`);
  }

  async generateWorkflow(prompt: string) {
    try {
      // Set a reasonable timeout for the external AI service call (e.g., 30 seconds)
      const response = await axios.post(`${this.pythonApi}/generate`, { prompt }, { timeout: 30000 });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError;
      
      // 1. Handle HTTP errors from the Python API (e.g., 500 from FastAPI)
      if (axiosError.response) {
        const statusCode = axiosError.response.status;
        // The Python backend is designed to return the error detail in 'detail'
        const detail = (axiosError.response.data as any)?.detail || 'AI Engine processing error';
        
        this.logger.error(`AI Engine failed with ${statusCode}: ${detail}`);
        
        // Pass the specific error detail back to the client
        throw new HttpException(
          `Workflow generation failed: ${detail}`, 
          HttpStatus.INTERNAL_SERVER_ERROR
        );
      } 
      
      // 2. Handle network/timeout errors
      else if (axiosError.code === 'ECONNABORTED' || axiosError.code === 'ECONNREFUSED' || axiosError.code === 'ENOTFOUND') {
        this.logger.error(`Connection error to Python API: ${this.pythonApi}`);
        throw new HttpException(
          'AI Engine is unavailable or timed out (30s limit). Please check the Python service.',
          HttpStatus.SERVICE_UNAVAILABLE
        );
      }
      
      // 3. Fallback for unexpected errors
      else {
        this.logger.error(`Unexpected error during workflow generation: ${axiosError.message}`);
        throw new HttpException('An unexpected server error occurred.', HttpStatus.INTERNAL_SERVER_ERROR);
      }
    }
  }
}